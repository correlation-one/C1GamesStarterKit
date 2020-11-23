package com.c1games.terminal.starteralgo;

import com.c1games.terminal.algo.*;
import com.c1games.terminal.algo.io.GameLoop;
import com.c1games.terminal.algo.io.GameLoopDriver;
import com.c1games.terminal.algo.map.GameState;
import com.c1games.terminal.algo.map.MapBounds;
import com.c1games.terminal.algo.map.Unit;
import com.c1games.terminal.algo.units.UnitType;

import java.util.*;

/**
 * Java implementation of the standard starter algo.
 */
public class StarterAlgo implements GameLoop {
    public static void main(String[] args) {
        new GameLoopDriver(new StarterAlgo()).run();
    }

    private static final Coords[] wallProtectTurrets = {
            new Coords(8, 12),
            new Coords(19, 12)
    };

    private static final Coords[] defensiveTurretLocations = {
            new Coords(0, 13),
            new Coords(27, 13),
            new Coords(8, 11),
            new Coords(19, 11),
            new Coords(13, 11),
            new Coords(14, 11)
    };

    private static final Coords[] supportLocations = {
            new Coords(13, 2),
            new Coords(14, 2),
            new Coords(13, 3),
            new Coords(14, 3)
    };

    private final Random rand = new Random();

    private ArrayList<Coords> scoredOnLocations = new ArrayList<>();

    @Override
    public void initialize(GameIO io, Config config) {
        GameIO.debug().println("Configuring your custom java algo strategy...");
        long seed = rand.nextLong();
        rand.setSeed(seed);
        GameIO.debug().println("Set random seed to: " + seed);
    }

    /**
     * Make a move in the game.
     */
    @Override
    public void onTurn(GameIO io, GameState move) {
        GameIO.debug().println("Performing turn " + move.data.turnInfo.turnNumber + " of your custom algo strategy");

        buildDefenses(move);
        buildReactiveDefenses(move);

        if (move.data.turnInfo.turnNumber < 5) {
            deployRandomInterceptors(move);
        } else {
            // If they have a lot of units in the first two of their rows, we can use the long range Demolisher to deal damage to them
            if (detectEnemyUnits(move,null, List.of(14,15), null) > 10) {
                demolisherLineStrategy(move);
            }
            // Otherwise lets go with a scout rush strategy where we send a ton of fast scoring units.
            else {
                // We only send scouts every other turn because its better to save up for a big attack.
                if (move.data.turnInfo.turnNumber % 2 == 1) {
                    // Lets dynamically choose which side to attack based on the expected path the units will take
                    Coords bestLoc = leastDamageSpawnLocation(move, List.of(new Coords(13, 0), new Coords(14, 0)));
                    for (int i = 0; i < 100; i++) {
                        move.attemptSpawn(bestLoc,UnitType.Scout);
                    }
                }
                // Lastly, lets build Supports
                move.attemptSpawnMultiple(Arrays.asList(supportLocations),UnitType.Support);
            }
        }
    }

    /**
     * Save process action frames. Careful there are many action frames per turn!
     */
    @Override
    public void onActionFrame(GameIO io, GameState move) {
        // Save locations that the enemy scored on against us to reactively build defenses
        for (FrameData.Events.BreachEvent breach : move.data.events.breach) {
            if (breach.unitOwner != PlayerId.Player1) {
                scoredOnLocations.add(breach.coords);
            }
        }
    }

    // Once the C1 logo is made, attempt to build some defenses.
    private void buildDefenses(GameState move) {
        // First lets protect ourselves a little with turrets.
        move.attemptSpawnMultiple(Arrays.asList(defensiveTurretLocations), UnitType.Turret);
        // Lets protect our turrets with some walls.
        move.attemptSpawnMultiple(Arrays.asList(wallProtectTurrets), UnitType.Wall);
        // Lastly, lets upgrade those important walls that protect our turrets.
        move.attemptUpgradeMultiple(Arrays.asList(wallProtectTurrets));
    }

    /**
     * Build defenses reactively based on where we got scored on
     */
    private void buildReactiveDefenses(GameState move) {
        for (Coords loc : scoredOnLocations) {
            // Build 1 space above the breach location so that it doesn't block our spawn locations
            move.attemptSpawn(new Coords(loc.x, loc.y +1), UnitType.Turret);
        }
    }

    /**
     * Deploy offensive units.
     */
    private void deployRandomInterceptors(GameState move) {
        /*
        Lets send out Interceptors to help destroy enemy mobile units.
        A complex algo would predict where the enemy is going to send units and
        develop its strategy around that. But this algo is simple so lets just
        send out interceptors in random locations and hope for the best.

        Mobile units can only deploy on our edges. 
        So lets get a list of those locations.
         */
        List<Coords> friendlyEdges = new ArrayList<>();
        friendlyEdges.addAll(Arrays.asList(MapBounds.EDGE_LISTS[MapBounds.EDGE_BOTTOM_LEFT]));
        friendlyEdges.addAll(Arrays.asList(MapBounds.EDGE_LISTS[MapBounds.EDGE_BOTTOM_RIGHT]));

        /*
        While we have remaining bits to spend lets send out interceptors randomly.
        */
        while (move.numberAffordable(UnitType.Interceptor) >= 1) {
            Coords c = friendlyEdges.get(rand.nextInt(friendlyEdges.size()));
            move.attemptSpawn(c, UnitType.Interceptor);
            /*
            We don't have to remove the location since multiple mobile units can occupy the same space. 
            Note that if all edge locations are blocked this will infinite loop!
             */
        }
    }

    /**
     * Goes through the list of locations, gets the path taken from them,
     * and loosely calculates how much damage will be taken by traveling that path assuming speed of 1.
     * @param move
     * @param locations
     * @return
     */
    private Coords leastDamageSpawnLocation(GameState move, List<Coords> locations) {
        List<Float> damages = new ArrayList<>();

        for (Coords location : locations) {
            List<Coords> path = move.pathfind(location, MapBounds.getEdgeFromStart(location));
            float totalDamage = 0;
            for (Coords dmgLoc : path) {
                List<Unit> attackers = move.getAttackers(dmgLoc);
                for (Unit unit : attackers) {
                    totalDamage += unit.unitInformation.attackDamageWalker.orElse(0);
                }
            }
            GameIO.debug().println("Got dmg:" + totalDamage + " for " + location);
            damages.add(totalDamage);
        }

        int minIndex = 0;
        float minDamage = 9999999;
        for (int i = 0; i < damages.size(); i++) {
            if (damages.get(i) <= minDamage) {
                minDamage = damages.get(i);
                minIndex = i;
            }
        }
        return locations.get(minIndex);
    }

    /**
     * Counts the number of a units found with optional parameters to specify what locations and unit types to count.
     * @param move GameState
     * @param xLocations Can be null, list of x locations to check for units
     * @param yLocations Can be null, list of y locations to check for units
     * @param units Can be null, list of units to look for, null will check all
     * @return count of the number of units seen at the specified locations
     */
    private int detectEnemyUnits(GameState move, List<Integer> xLocations, List<Integer> yLocations, List<UnitType> units) {
        if (xLocations == null) {
            xLocations = new ArrayList<Integer>();
            for (int x = 0; x < MapBounds.BOARD_SIZE; x++) {
                xLocations.add(x);
            }
        }
        if (yLocations == null) {
            yLocations = new ArrayList<Integer>();
            for (int y = 0; y < MapBounds.BOARD_SIZE; y++) {
                yLocations.add(y);
            }
        }

        if (units == null) {
            units = new ArrayList<>();
            for (Config.UnitInformation unit : move.config.unitInformation) {
                if (unit.startHealth.isPresent()) {
                    units.add(move.unitTypeFromShorthand(unit.shorthand.get()));
                }
            }
        }

        int count = 0;
        for (int x : xLocations) {
            for (int y : yLocations) {
                Coords loc = new Coords(x,y);
                if (MapBounds.inArena(loc)) {
                    for (Unit u : move.allUnits[x][y]) {
                        if (units.contains(u.type)) {
                            count++;
                        }
                    }
                }
            }
        }
        return count;
    }

    private void demolisherLineStrategy(GameState move) {
        /*
        First lets find the cheapest structure. We could hardcode this to "Wall",
        but lets demonstrate how to use java-algo features.
         */
        Config.UnitInformation cheapestUnit = null;
        for (Config.UnitInformation uinfo : move.config.unitInformation) {
            if (uinfo.unitCategory.isPresent() && move.isStructure(uinfo.unitCategory.getAsInt())) {
                float[] costUnit = uinfo.cost();
                if((cheapestUnit == null || costUnit[0] + costUnit[1] <= cheapestUnit.cost()[0] + cheapestUnit.cost()[1])) {
                    cheapestUnit = uinfo;
                }
            }
        }
        if (cheapestUnit == null) {
            GameIO.debug().println("There are no structures?");
        }

        for (int x = 27; x>=5; x--) {
            move.attemptSpawn(new Coords(x, 11), move.unitTypeFromShorthand(cheapestUnit.shorthand.get()));
        }

        for (int i = 0; i<22; i++) {
            move.attemptSpawn(new Coords(24, 10), UnitType.Demolisher);
        }
    }

}
