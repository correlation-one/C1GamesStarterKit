package com.c1games.terminal.algo.pathfinding;

import com.c1games.terminal.algo.Coords;
import com.c1games.terminal.algo.GameIO;
import com.c1games.terminal.algo.map.MapBounds;
import com.c1games.terminal.algo.map.GameState;

import java.util.*;
import java.util.stream.Collectors;

import static com.c1games.terminal.algo.map.MapBounds.*;

/**
 * This class computes data pertaining to the pathfinding from a particular point on the board, based on the random
 * access representation of the board created by movebuilder. As such, an instance of this class can be used to compute
 * the paths that certain units will move along, and is guarenteed to match the behavior of the actual game engine.
 * <p>
 * While this pathfinding is correct, it is not maximally optimized. Improving the efficiency of pathfinding is a task
 * left to the user.
 */
public class Pathfinder {
    private final static class Node {
        boolean visitedIdealness;
        boolean visitedValidate;
        boolean blocked;
        int pathlength;

        public Node(boolean blocked) {
            this.visitedIdealness = false;
            this.visitedValidate = false;
            this.blocked = blocked;
            this.pathlength = -1;
        }
    }

    private static final int DIRECTION_NULL = 0;
    private static final int DIRECTION_HORIZONTAL = 1;
    private static final int DIRECTION_VERTICAL = 2;

    private final GameState board;
    private final Coords start;
    private final int movementDirection;
    private final Node[][] grid;

    public Pathfinder(GameState board, Coords start, int movementDirection) throws IllegalPathStartException {
        if (!MapBounds.inArena(start))
            throw new IllegalPathStartException(IllegalPathStart.OutsideOfArena);
        if (board.getWallAt(start) != null)
            throw new IllegalPathStartException(IllegalPathStart.BlockedByWall);

        this.board = board;
        this.start = start;
        this.movementDirection = movementDirection;

        // create the grid, with the walls filled in
        grid = new Node[BOARD_SIZE][];
        for (int x = 0; x < BOARD_SIZE; x++) {
            grid[x] = new Node[BOARD_SIZE];
            for (int y = 0; y < BOARD_SIZE; y++) {
                grid[x][y] = new Node(board.getWallAt(new Coords(x, y)) != null);
            }
        }

        // perform the idealness search of the pocket
        List<Coords> idealTiles = idealnessSearch();

        // validate the pocket
        validate(idealTiles);

        // now the pathfinding query can be performed, and thus, the constructor leaves the object in a finish state
    }

    /**
     * Find the set of maximally ideal coords in this pocket
     */
    private List<Coords> idealnessSearch() {
        // short circuit if the start is on the edge
        if (IS_ON_EDGE[movementDirection][start.x][start.y])
            return edgeCoords();

        // set up variables
        Queue<Coords> queue = new LinkedList<>();
        queue.add(start);

        Coords bestTile = start;
        int bestIdealness = idealnessOf(start);

        // BFS the pocket
        while (!queue.isEmpty()) {
            Coords curr = queue.remove();
            List<Coords> neighborsToSearch = curr.neighbors().stream()
                    .filter(MapBounds::inArena)
                    .filter(neighbor -> board.getWallAt(neighbor) == null)
                    .collect(Collectors.toList());
            for (Coords neighbor : neighborsToSearch) {
                // don't enter an infinite loop
                if (grid[neighbor.x][neighbor.y].visitedIdealness)
                    continue;
                else
                    grid[neighbor.x][neighbor.y].visitedIdealness = true;

                // short circuit if we've reached the edge
                if (IS_ON_EDGE[movementDirection][neighbor.x][neighbor.y])
                    return edgeCoords();

                // otherwise, possible replacement
                int neighborIdealness = idealnessOf(neighbor);

                if (neighborIdealness > bestIdealness) {
                    bestIdealness = neighborIdealness;
                    bestTile = neighbor;
                }

                // and then recursion
                queue.add(neighbor);
            }
        }

        // if we reach the end without short circuiting, this pocket does not reach the edge
        return List.of(bestTile);
    }

    /**
     * Validate the nodes of the board so that proper pathfinding decisions can be made, given the ideal tiles
     * computed in idealnessSearch.
     */
    private void validate(List<Coords> idealTiles) {
        // set the first tiles' pathlength, mark them as validate-visited, and add them to a queue
        Queue<Coords> queue = new LinkedList<>();
        for (Coords idealTile : idealTiles) {
            grid[idealTile.x][idealTile.y].pathlength = 0;
            grid[idealTile.x][idealTile.y].visitedValidate = true;
            queue.add(idealTile);
        }

        // BFS the pocket
        while (!queue.isEmpty()) {
            Coords curr = queue.remove();
            List<Coords> neighborsToSearch = curr.neighbors().stream()
                    .filter(MapBounds::inArena)
                    .filter(neighbor -> board.getWallAt(neighbor) == null)
                    .collect(Collectors.toList());
            for (Coords neighbor : neighborsToSearch) {
                // don't enter an infinite loop
                if (grid[neighbor.x][neighbor.y].visitedValidate)
                    continue;
                else
                    grid[neighbor.x][neighbor.y].visitedValidate = true;

                // mark pathlength and recurse
                grid[neighbor.x][neighbor.y].pathlength = grid[curr.x][curr.y].pathlength + 1;
                queue.add(neighbor);
            }
        }
    }

    /**
     * The list of coords which are on the target edge, and not in walls.
     */
    private List<Coords> edgeCoords() {
        List<Coords> list = new ArrayList<>();
        for (int x = 0; x < BOARD_SIZE; x++) {
            for (int y = 0; y < BOARD_SIZE; y++) {
                if (IS_ON_EDGE[movementDirection][x][y] && !grid[x][y].blocked) {
                    list.add(new Coords(x, y));
                }
            }
        }
        return list;
    }

    /**
     * Get the idealness of a particular tile, as if that tile were the most ideal tile of the pocket.
     */
    private int idealnessOf(Coords tile) {
        if (IS_ON_EDGE[movementDirection][tile.x][tile.y]) {
            return Integer.MAX_VALUE;
        } else {
            int idealness = 0;
            if (movementDirection == EDGE_TOP_LEFT || movementDirection == EDGE_TOP_RIGHT)
                idealness += BOARD_SIZE * tile.y;
            else
                idealness += BOARD_SIZE * (BOARD_SIZE - 1 - tile.y);
            if (movementDirection == EDGE_TOP_RIGHT || movementDirection == EDGE_BOTTOM_RIGHT)
                idealness += tile.x;
            else
                idealness += (BOARD_SIZE - 1 - tile.x);
            return idealness;
        }
    }

    private static String justifyFormat(int n, int width) {
        StringBuilder builder = new StringBuilder();
        String nAsString = Integer.toString(n);
        for (int i = 0; i < width - nAsString.length(); i++) {
            builder.append(' ');
        }
        builder.append(nAsString);
        return builder.toString();
    }


    private void debugPrint() {
        final String WALL_TEXT = " []";
        final String INVALID_TEXT = "   ";
        final String OUTSIDE_TEXT = " **";
        for (int y = MapBounds.BOARD_SIZE - 1; y >= 0; y--) {
            System.err.print(justifyFormat(y, 3));
            for (int x = 0; x < MapBounds.BOARD_SIZE; x++) {
                Coords c = new Coords(x, y);
                if (!MapBounds.inArena(c))
                    System.err.print(OUTSIDE_TEXT);
                else if (grid[c.x][c.y].blocked)
                    System.err.print(WALL_TEXT);
                else if (grid[c.x][c.y].visitedValidate)
                    System.err.print(justifyFormat(grid[c.x][c.y].pathlength, 3));
                else
                    System.err.print(INVALID_TEXT);
            }
            System.err.println();
        }
        System.err.print("   ");
        for(int i = 0; i < MapBounds.BOARD_SIZE; i++){
            System.err.print(justifyFormat(i, 3));
        }
        System.err.println();
    }

    /**
     * Get the computed path that a unit at the start point will follow.
     */
    public List<Coords> getPath() {
        // debugPrint();

        List<Coords> path = new ArrayList<>();
        path.add(start);
        Coords curr = start;
        int currDirection = DIRECTION_NULL;

        // just follow the best path based on computed data until the end of the path is reached
        while (grid[curr.x][curr.y].pathlength != 0) {
            // get the next tile
            Coords next = nextMove(curr, currDirection);

            // update curr direction
            currDirection = directionDifference(curr, next);

            // build the list
            curr = next;
            path.add(next);
        }

        return path;
    }

    /**
     * Get the next move we will make at a certain point in the path.
     */
    private Coords nextMove(Coords curr, int currDirection) {
        // filter by validated tiles
        List<Coords> possible = curr.neighbors().stream()
                .filter(MapBounds::inArena)
                .filter(neighbor -> grid[neighbor.x][neighbor.y].visitedValidate)
                .collect(Collectors.toList());
        // filter by maximal pathlength, and select the tile which is directionally optimal
        int bestPathlength = possible.stream()
                .map(neighbor -> grid[neighbor.x][neighbor.y].pathlength)
                .min(Integer::compare)
                .get();
        return possible.stream()
                .filter(neighbor -> grid[neighbor.x][neighbor.y].pathlength == bestPathlength)
                .max(compareByDirectionalCorrectness(curr, currDirection))
                .get();
    }

    /**
     * Given two adjacent coords, return DIRECTION_VERTICAL or DIRECTION_HORIZONTAL based on their position relative to each other.
     */
    private static final int directionDifference(Coords from, Coords to) {
        if (from.x == to.x && from.y != to.y)
            return DIRECTION_VERTICAL;
        else if (from.x != to.x && from.y == to.y)
            return DIRECTION_HORIZONTAL;
        else
            throw new IllegalArgumentException("not adjacent: " + from + " and " + to);
    }

    /**
     * Given a current tile and previous move direction, produce a comparator which compares adjacent tiles by which is more optimal for
     * the next tile in pathfinding, based on the direction rules, without taking into account pathlength.
     */
    private Comparator<Coords> compareByDirectionalCorrectness(Coords curr, int currDirection) {
        return (option1, option2) -> {
            // find the directions
            int direction1 = directionDifference(curr, option1);
            int direction2 = directionDifference(curr, option2);

            // rule 3: if this is the first movement, they will want to move vertically
            {
                boolean good1 = currDirection == DIRECTION_NULL && direction1 == DIRECTION_VERTICAL;
                boolean good2 = currDirection == DIRECTION_NULL && direction2 == DIRECTION_VERTICAL;
                if (good2 && !good1) {
                    //System.err.println("case 1a " + curr + " -> " + option1);
                    return -1;
                } else if (good1 && !good2) {
                    //System.err.println("case 1b " + curr + " -> " + option1);
                    return 1;
                }
            }

            // rule 2: we want to change direction
            {
                boolean good1 = currDirection != direction1;
                boolean good2 = currDirection != direction2;
                if (good2 && !good1) {
                    //System.err.println("case 2a " + curr + " -> " + option1);
                    return -1;
                } else if (good1 && !good2) {
                    //System.err.println("case 2b " + curr + " -> " + option1);
                    return 1;
                }
            }

            // rule 4: move towards target edge
            if ((movementDirection == EDGE_TOP_RIGHT && (option2.x > option1.x || option2.y > option1.y)) ||
                    (movementDirection == EDGE_TOP_LEFT && (option2.x < option1.x || option2.y > option1.y)) ||
                    (movementDirection == EDGE_BOTTOM_RIGHT && (option2.x > option1.x || option2.y < option1.y)) ||
                    (movementDirection == EDGE_BOTTOM_LEFT && (option2.x < option1.x || option2.y < option1.y))) {
                //System.err.println("case 3a " + curr + " -> " + option1);
                return -1;
            } else {
                //System.err.println("case 3b " + curr + " -> " + option1);
                return 1;
            }
        };
    }


}
