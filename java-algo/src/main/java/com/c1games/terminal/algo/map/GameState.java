package com.c1games.terminal.algo.map;

import com.c1games.terminal.algo.Config;
import com.c1games.terminal.algo.Coords;
import com.c1games.terminal.algo.FrameData;
import com.c1games.terminal.algo.PlayerId;
import com.c1games.terminal.algo.pathfinding.IllegalPathStartException;
import com.c1games.terminal.algo.pathfinding.Pathfinder;
import com.c1games.terminal.algo.units.UnitType;

import java.util.ArrayList;
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
    private final class UnitList {
        final List<Unit> list = new ArrayList<>();
    }

    public final Config config;
    public final FrameData data;

    private Unit[][] walls; // nullable
    private Unit[][] remove;
    private UnitList[][] info;

    private List<SpawnCommand> buildStack = new ArrayList<>();
    private List<SpawnCommand> deployStack = new ArrayList<>();

    public GameState(Config config, FrameData data) {
        this.config = config;
        this.data = data;

        // create the grids
        walls = new Unit[MapBounds.BOARD_SIZE][MapBounds.BOARD_SIZE];
        remove = new Unit[MapBounds.BOARD_SIZE][MapBounds.BOARD_SIZE];
        info = new UnitList[MapBounds.BOARD_SIZE][MapBounds.BOARD_SIZE];
        for (int i = 0; i < MapBounds.BOARD_SIZE; i++) {
            for (int j = 0; j < MapBounds.BOARD_SIZE; j++) {
                info[i][j] = new UnitList();
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
                    info[unit.x][unit.y].list.add(new Unit(type, unit.stability, unit.unitId, player));
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
                    if (walls[unit.x][unit.y] != null)
                        System.err.println("Error: multiple walls at (" + unit.x + ", " + unit.y + ")");
                    walls[unit.x][unit.y] = new Unit(type, unit.stability, unit.unitId, player);
                }
            }

            // fill in the remove units
            for (FrameData.PlayerUnit unit : units.remove) {
                if (remove[unit.x][unit.y] != null)
                    System.err.println("Error: multiple remove at (" + unit.x + ", " + unit.y + ")");
                remove[unit.x][unit.y] = new Unit(UnitType.Remove, unit.stability, unit.unitId, player);
            }
        }
    }

    public List<Unit> getInfoAt(Coords coords) {
        return info[coords.x][coords.y].list;
    }

    /**
     * Nullable.
     */
    public Unit getWallAt(Coords coords) {
        return walls[coords.x][coords.y];
    }

    /**
     * Nullable.
     *
     * Only checks whether there is a remove unit at that particular location, denoting whether we have removed a firewall at that unit.
     * Does not actually remove the unit.
     */
    public Unit getRemoveAt(Coords coords) {
        return remove[coords.x][coords.y];
    }

    /**
     * Result of whether a unit can be spawned at a location.
     */
    public CanSpawn canSpawn(Coords coords, UnitType type, int quantity) {
        if (numberAffordable(type) < quantity)
            return CanSpawn.NotEnoughResources;
        if (type != UnitType.Remove && getWallAt(coords) != null)
            return CanSpawn.UnitAlreadyPresent;
        if (type.isFirewall() && !getInfoAt(coords).isEmpty())
            return CanSpawn.UnitAlreadyPresent;
        if (coords.y >= MapBounds.BOARD_SIZE / 2)
            return CanSpawn.WrongSideOfMap;
        if (!MapBounds.inArena(coords))
            return CanSpawn.OutOfBounds;
        if (type.isInfo() && !(MapBounds.IS_ON_EDGE[MapBounds.EDGE_BOTTOM_LEFT][coords.x][coords.y] ||
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
        // check the ability to spawn
        CanSpawn canSpawn = canSpawn(coords, type, 1);
        if (!canSpawn.affirmative())
            throw new CannotSpawnException(canSpawn);

        // subtract the cost from the data
        float cost = ((Config.RealUnitInformation) config.unitInformation.get(type.ordinal())).cost();
        if (type.isInfo())
            data.p1Stats.bits -= cost;
        else if (type.isFirewall())
            data.p1Stats.cores -= cost;

        // add the unit to the data
        Unit unit = new Unit(type, 1, "spawned", PlayerId.Player1);
        if (type.isFirewall())
            walls[coords.x][coords.y] = unit;
        else if (type.isInfo())
            info[coords.x][coords.y].list.add(unit);
        else
            remove[coords.x][coords.y] = unit;

        // add it to the stack of spawn commands to send in
        SpawnCommand command = new SpawnCommand(type, coords.x, coords.y);
        if (type.isFirewall() || type == UnitType.Remove)
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
        if (!info[coords.x][coords.y].list.isEmpty())
            return CanRemove.InfoUnitPresent;
        if (walls[coords.x][coords.y] == null)
            return CanRemove.NoUnitPresent;
        return CanRemove.Yes;
    }

    /**
     * Attempt to remove an existing firewall that we own, or throw an exception is unable.
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

        // clear the tower from the map
        UnitType type = walls[coords.x][coords.y].type;
        walls[coords.x][coords.y] = null;

        // add the remove unit from the map
        remove[coords.x][coords.y] = new Unit(UnitType.Remove, 1, "removed", PlayerId.Player1);

        // refund the cost
        float refund = ((Config.RealUnitInformation) config.unitInformation.get(type.ordinal())).cost();
        if (type.isInfo())
            data.p1Stats.bits += refund;
        else if (type.isFirewall())
            data.p1Stats.cores += refund;
        else
            throw new RuntimeException("unreachable");

        // add it to the stack of commands to send in
        buildStack.add(new SpawnCommand(UnitType.Remove, coords.x, coords.y));
    }

    /**
     * How many of a certain unit type we can afford.
     */
    public int numberAffordable(UnitType type) {
        float cost = ((Config.RealUnitInformation) config.unitInformation.get(type.ordinal())).cost();
        float wealth;
        if (type.isInfo())
            wealth = data.p1Stats.bits;
        else if (type.isFirewall())
            wealth = data.p1Stats.cores;
        else
            throw new IllegalArgumentException("Cannot query number affordable of remove unit type");
        return (int) (wealth / cost);
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
}
