package com.c1games.terminal.algo.map;

import com.c1games.terminal.algo.*;
import com.c1games.terminal.algo.pathfinding.IllegalPathStartException;
import com.c1games.terminal.algo.pathfinding.Pathfinder;
import com.c1games.terminal.algo.units.UnitType;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.InvalidPropertiesFormatException;
import java.util.List;

/**
 * An object derived from frame data which can be used to compose a move, before eventually sending it into the GameIO object.
 *
 * This object contains a random-access representation of the map state and all its units, which can be used to query for information about the
 * game, including move legality.
 *
 * This object keeps a buffer of unit placements, which will be serialized and sent to the game engine upon making of the move.
 */
public class GameState {
    public static final int TowerUnitCategory = 0; // tower units
    public static final int WalkerUnitCategory = 1; // info units
    public final Config config;
    public final FrameData data;

    //private Unit[][] walls; // nullable
    //private Unit[][] remove;
    public List<Unit>[][] allUnits;

    private List<SpawnCommand> buildStack = new ArrayList<>();
    private List<SpawnCommand> deployStack = new ArrayList<>();

    public GameState(Config config, FrameData data) {
        this.config = config;
        this.data = data;

        // create the grids
        //walls = new Unit[MapBounds.BOARD_SIZE][MapBounds.BOARD_SIZE];
        //remove = new Unit[MapBounds.BOARD_SIZE][MapBounds.BOARD_SIZE];
        allUnits = new ArrayList[MapBounds.BOARD_SIZE][MapBounds.BOARD_SIZE];
        for (int i = 0; i < MapBounds.BOARD_SIZE; i++) {
            for (int j = 0; j < MapBounds.BOARD_SIZE; j++) {
                allUnits[i][j] = new ArrayList<Unit>();
            }
        }

        // for each player
        for (PlayerId player : List.of(PlayerId.Player1, PlayerId.Player2)) {
            FrameData.PlayerUnits units;
            if (player == PlayerId.Player1)
                units = data.p1Units;
            else if (player == PlayerId.Player2)
                units = data.p2Units;
            else
                throw new RuntimeException("unreachable");

            // fill in the info units
            for (UnitType type : List.of(UnitType.Ping, UnitType.EMP, UnitType.Scrambler)) {
                List<FrameData.PlayerUnit> list;
                if (type == UnitType.Ping)
                    list = units.ping;
                else if (type == UnitType.EMP)
                    list = units.emp;
                else if (type == UnitType.Scrambler)
                    list = units.scrambler;
                else
                    throw new RuntimeException("unreachable");

                for (FrameData.PlayerUnit unit : list) {
                    allUnits[unit.x][unit.y].add(new Unit(type, unit.stability, unit.unitId, player, config));
                }
            }

            // fill in the wall units
            for (UnitType type : List.of(UnitType.Filter, UnitType.Encryptor, UnitType.Destructor)) {
                List<FrameData.PlayerUnit> list;
                if (type == UnitType.Filter)
                    list = units.filter;
                else if (type == UnitType.Encryptor)
                    list = units.encryptor;
                else if (type == UnitType.Destructor)
                    list = units.destructor;
                else
                    throw new RuntimeException("unreachable");

                for (FrameData.PlayerUnit unit : list) {
                    allUnits[unit.x][unit.y].add(new Unit(type, unit.stability, unit.unitId, player, config));
                }
            }

            // fill in the remove units
            for (FrameData.PlayerUnit unit : units.remove) {
                Unit wall = getWallAt(new Coords(unit.x, unit.y));
                if (wall != null) {
                    wall.removing = true;
                }
            }

            // fill in the upgraded units
            for (FrameData.PlayerUnit unit : units.upgrade) {
                Unit wall = getWallAt(new Coords(unit.x, unit.y));
                if (wall != null) {
                    wall.upgrade();
                }
            }
        }
    }

    /**
     * Could return empty list
     */
    public List<Unit> getInfoAt(Coords coords) {
        List<Unit> ret = new ArrayList<>();
        for (Unit unit : allUnits[coords.x][coords.y]) {
            if (unit.unitInformation.unitCategory.getAsInt() == WalkerUnitCategory) {
                ret.add(unit);
            }
        }
        return ret;
    }

    public boolean isFirewall(UnitType type) {
        return config.unitInformation.get(type.ordinal()).unitCategory.orElse(-1) == TowerUnitCategory;
    }

    public boolean isInfo(UnitType type) {
        return config.unitInformation.get(type.ordinal()).unitCategory.orElse(-1) == WalkerUnitCategory;
    }

    public boolean isFirewall(int category) {
        return category == TowerUnitCategory;
    }

    public boolean isInfo(int category) {
        return category == WalkerUnitCategory;
    }

    public UnitType unitTypeFromShorthand(String shorthand) {
        for (int i = 0; i < config.unitInformation.size(); i++) {
            if (config.unitInformation.get(i).shorthand.orElse("").equalsIgnoreCase(shorthand)) {
                return UnitType.values()[i];
            }
        }
        return null;
    }

    /**
     * Nullable.
     */
    public Unit getWallAt(Coords coords) {
        for (Unit unit : allUnits[coords.x][coords.y]) {
            if (unit.unitInformation.unitCategory.getAsInt() == TowerUnitCategory) {
                return unit;
            }
        }
        return null;
    }

    /**
     * Nullable.
     *
     * Only checks whether there is a remove unit at that particular location, denoting whether we have removed a firewall at that unit.
     * Does not actually remove the unit.
     */
    public boolean getRemoveAt(Coords coords) {
        return getWallAt(coords) != null && getWallAt(coords).removing;
    }

    /**
     * Result of whether a unit can be spawned at a location.
     */
    public CanSpawn canSpawn(Coords coords, UnitType type, int quantity) {
        if (type != UnitType.Upgrade && numberAffordable(type, false) < quantity)
            return CanSpawn.NotEnoughResources;
        if (type != UnitType.Remove && type != UnitType.Upgrade && getWallAt(coords) != null)
            return CanSpawn.UnitAlreadyPresent;
        if (type == UnitType.Upgrade && getWallAt(coords) == null)
            return CanSpawn.NoUnitPresent;
        if (type == UnitType.Upgrade && getWallAt(coords).upgraded)
            return CanSpawn.UnitAlreadyPresent;
        if (type == UnitType.Upgrade && numberAffordable(getWallAt(coords).type, true) < quantity)
            return CanSpawn.NotEnoughResources;
        if (isFirewall(type) && !getInfoAt(coords).isEmpty())
            return CanSpawn.UnitAlreadyPresent;
        if (coords.y >= MapBounds.BOARD_SIZE / 2)
            return CanSpawn.WrongSideOfMap;
        if (!MapBounds.inArena(coords))
            return CanSpawn.OutOfBounds;
        if (isInfo(type) && !(MapBounds.IS_ON_EDGE[MapBounds.EDGE_BOTTOM_LEFT][coords.x][coords.y] ||
                MapBounds.IS_ON_EDGE[MapBounds.EDGE_BOTTOM_RIGHT][coords.x][coords.y]))
            return CanSpawn.NotOnEdge;
        return CanSpawn.Yes;
    }

    /**
     * Attempt to spawn a unit at a location, or throw an exception if unable.
     *
     * This will alter the data within GameState and FrameData as if this operation proceeded (unless an exception is thrown) so that further
     * operations can be applied correctly.
     *
     * This should be paired with @code canSpawn to avoid the exception.
     */
    public void spawn(Coords coords, UnitType type) throws CannotSpawnException {
        if (type == UnitType.Remove) {
            throw new IllegalArgumentException("Cannot spawn removal use attemptRemoveFirewall function instead");
        }
        if (type == UnitType.Upgrade) {
            throw new IllegalArgumentException("Cannot spawn upgrade use attemptUpgrade function instead");
        }

        // check the ability to spawn
        CanSpawn canSpawn = canSpawn(coords, type, 1);
        if (!canSpawn.affirmative())
            throw new CannotSpawnException(canSpawn);

        // subtract the cost from the data
        float[] cost = ((Config.RealUnitInformation) config.unitInformation.get(type.ordinal())).cost();
        data.p1Stats.bits -= cost[1];
        data.p1Stats.cores -= cost[0];

        // add the unit to the data
        Unit unit = new Unit(type, 1, "spawned", PlayerId.Player1, config);
        allUnits[coords.x][coords.y].add(unit);



        // add it to the stack of spawn commands to send in
        SpawnCommand command = new SpawnCommand(type, coords.x, coords.y);
        if (isFirewall(type))
            buildStack.add(command);
        else
            deployStack.add(command);
    }

    /**
     * Spawn a unit in a location if able, returning whether it successfully spawned the unit.
     */
    public boolean attemptSpawn(Coords location, UnitType type) {
        if (canSpawn(location, type, 1).affirmative()) {
            spawn(location, type);
            return true;
        } else {
            return false;
        }
    }

    /**
     * Spawn a certain unit type in as many locations as possible, returning the number successful.
     */
    public int attemptSpawnMultiple(List<Coords> locations, UnitType type) {
        int successful = 0;
        for (Coords c : locations) {
            if (canSpawn(c, type, 1).affirmative()) {
                spawn(c, type);
                successful++;
            }
        }
        return successful;
    }

    /**
     * Result of whether a firewall can be removed at a location.
     */
    public CanRemove canRemoveFirewall(Coords coords) {
        if (!MapBounds.ARENA[coords.x][coords.y])
            return CanRemove.OutOfBounds;
        if (coords.y >= MapBounds.BOARD_SIZE / 2)
            return CanRemove.WrongSideOfMap;
        if (getWallAt(coords) == null)
            return CanRemove.NoUnitPresent;
        return CanRemove.Yes;
    }

    /**
     * Attempt to remove an existing firewall that we own, or throw an exception if unable.
     *
     * This will alter the data within GameState and FrameData as if this operation proceeded (unless an exception is thrown) so that further
     * operations can be applied correctly.
     *
     * This should be paired with @code canRemove to avoid the exception.
     */
    public void removeFirewall(Coords coords) throws CannotRemoveException {
        // check the ability to remove
        CanRemove canRemove = canRemoveFirewall(coords);
        if (!canRemove.affirmative())
            throw new CannotRemoveException(canRemove);

        getWallAt(coords).removing = true;

        // add it to the stack of commands to send in
        buildStack.add(new SpawnCommand(UnitType.Remove, coords.x, coords.y));
    }

    public int attemptRemoveFirewall(Coords coords) {
        int successful = 0;
        if (canRemoveFirewall(coords).affirmative()) {
            removeFirewall(coords);
            successful++;
        }
        return successful;
    }

    public int attemptRemoveFirewallMultiple(List<Coords> coords) {
        int successful = 0;
        for (Coords c : coords) {
            successful += attemptRemoveFirewall(c);
        }
        return successful;
    }

    public int attemptUpgrade(Coords coords) {
        int successful = 0;
        if (canSpawn(coords, UnitType.Upgrade, 1).affirmative() && numberAffordable(getWallAt(coords).type, true) >= 1) {
            placeUpgrade(coords);
            successful++;
        }
        return successful;
    }

    public int attemptUpgradeMultiple(List<Coords> coords) {
        int successful = 0;
        for (Coords c : coords) {
            successful += attemptUpgrade(c);
        }
        return successful;
    }

    public void placeUpgrade(Coords loc) {
        Unit toUpgrade = getWallAt(loc);
        float[] cost = toUpgrade.unitInformation.cost();
        Config.UnitInformation upgradeInfo = toUpgrade.unitInformation.upgrade.orElse(null);
        if (upgradeInfo != null) {
            cost[0] = (float)upgradeInfo.cost1.orElse(cost[0]);
            cost[1] = (float)upgradeInfo.cost2.orElse(cost[1]);
        } else {
            throw new IllegalArgumentException("Cannot upgrade this way, unit not upgradeable: " + loc);
        }

        data.p1Stats.bits -= cost[1];
        data.p1Stats.cores -= cost[0];

        toUpgrade.upgrade();

        buildStack.add(new SpawnCommand(UnitType.Upgrade, loc.x, loc.y));
    }

    /**
     * How many of a certain unit type we can afford.
     */
    public int numberAffordable(UnitType type, boolean upgrade) {
        if (type == UnitType.Remove) {
            throw new IllegalArgumentException("Cannot query number affordable of remove unit type use removeFirewall");
        }
        if (type == UnitType.Upgrade) {
            throw new IllegalArgumentException("Cannot query number affordable of upgrades this way, put type of unit to upgrade and upgrade=true");
        }

        float[] cost = ((Config.RealUnitInformation) config.unitInformation.get(type.ordinal())).cost();
        if (upgrade) {
            Config.UnitInformation upgradeInfo = config.unitInformation.get(type.ordinal()).upgrade.orElse(null);
            if (upgradeInfo != null) {
                cost[0] = (float)upgradeInfo.cost1.orElse(cost[0]);
                cost[1] = (float)upgradeInfo.cost2.orElse(cost[1]);
            } else {
                throw new IllegalArgumentException("Cannot query number affordable of upgrades this way, unit not upgradeable");
            }
        }

        float[] wealth = new float[] { data.p1Stats.cores, data.p1Stats.bits };
        int[] afford = new int[] {
                cost[0] > 0 ?  (int) (wealth[0]/cost[0]) : 99,
                cost[1] > 0 ?  (int) (wealth[1]/cost[1]) : 99,
        };

        return Math.min(afford[0], afford[1]);
    }

    /**
     * How many of a certain unit type we can afford.
     */
    public int numberAffordable(UnitType type) {
        return numberAffordable(type, false);
    }

    /**
     * Get the spawn commands necessary to submit to the engine to take this turn.
     *
     * This is generally used by implementations of gameio.
     */
    public List<List<SpawnCommand>> getSpawnCommands() {
        return List.of(buildStack, deployStack);
    }

    /**
     * Use the code within the pathfinding package to compute the path that an info unit would take if placed on a particular coordinate,
     * assuming that the layout of the walls do not change.
     *
     * Throws an IllegalPathStartExceptions if a unit could not be placed in that location.s
     */
    public List<Coords> pathfind(Coords start, int targetEdge) throws IllegalPathStartException {
        return new Pathfinder(this, start, targetEdge).getPath();
    }

    public List<Unit> getAttackers(Coords coords) {
        List<Unit> attackers = new ArrayList<>();
        if (!MapBounds.inArena(coords)) {
            GameIO.debug().println("Checking attackers out of bounds! " + coords);
        }

        float maxRange = 0;
        float maxGetHit = 0;
        for (Config.UnitInformation uinfo : config.unitInformation) {
            if (uinfo.unitCategory.orElse(999) == TowerUnitCategory && uinfo.attackRange.orElse(0) > maxRange) {
                maxRange = (float) uinfo.attackRange.getAsDouble();
            }
            if (uinfo.getHitRadius.orElse(0) > maxGetHit) {
                maxGetHit = (float)uinfo.getHitRadius.getAsDouble();
            }
        }

        int max = (int)Math.ceil(maxRange);

        for (int x = coords.x - max; x <= coords.x + max; x++) {
            for (int y = coords.y - max; y <= coords.y + max; y++) {
                Coords c = new Coords(x,y);
                if (MapBounds.inArena(c)) {
                    Unit unit = getWallAt(c);
                    if (unit != null && unit.owner == PlayerId.Player2 && unit.unitInformation.attackRange.isPresent()
                            && c.distance(coords) <= unit.unitInformation.attackRange.orElse(0) + maxGetHit) {
                        attackers.add(unit);
                    }
                }
            }
        }

        return attackers;
    }
}
