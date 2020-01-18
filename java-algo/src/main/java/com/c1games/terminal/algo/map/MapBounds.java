package com.c1games.terminal.algo.map;

import com.c1games.terminal.algo.Coords;

/**
 * Static constants representing the constant status of different tiles on the map, such as whether it is on an edge, on on the board.
 */
public class MapBounds {
    public static final int BOARD_SIZE = 28;

    private MapBounds() {
    }

    public static final int EDGE_TOP_RIGHT = 0;
    public static final int EDGE_TOP_LEFT = 1;
    public static final int EDGE_BOTTOM_LEFT = 2;
    public static final int EDGE_BOTTOM_RIGHT = 3;

    /**
     * For each direction constant, declared above, a boolean grid denoting whether this cell is on the corresponding edge.
     */
    public static final boolean[][][] IS_ON_EDGE;
    /**
     * For each direction constant, declared above, an array of all the coordinates which compose that edge.
     */
    public static final Coords[][] EDGE_LISTS;
    static {
        // Fill in the edges with the same logic from python starter algo.
        IS_ON_EDGE = new boolean[4][BOARD_SIZE][BOARD_SIZE];
        EDGE_LISTS = new Coords[4][BOARD_SIZE / 2];
        for (int i = 0; i < BOARD_SIZE / 2; i++) {
            Coords c = new Coords(BOARD_SIZE / 2 + i, BOARD_SIZE - 1 - i);
            IS_ON_EDGE[EDGE_TOP_RIGHT][c.x][c.y] = true;
            EDGE_LISTS[EDGE_TOP_RIGHT][i] = c;
        }
        for (int i = 0; i < BOARD_SIZE / 2; i++) {
            Coords c = new Coords(BOARD_SIZE / 2 - 1 - i, BOARD_SIZE - 1 - i);
            IS_ON_EDGE[EDGE_TOP_LEFT][c.x][c.y] = true;
            EDGE_LISTS[EDGE_TOP_LEFT][i] = c;
        }
        for (int i = 0; i < BOARD_SIZE / 2; i++) {
            Coords c = new Coords(BOARD_SIZE / 2 - 1 - i, i);
            IS_ON_EDGE[EDGE_BOTTOM_LEFT][c.x][c.y] = true;
            EDGE_LISTS[EDGE_BOTTOM_LEFT][i] = c;
        }
        for (int i = 0; i < BOARD_SIZE / 2; i++) {
            Coords c = new Coords(BOARD_SIZE / 2 + i, i);
            IS_ON_EDGE[EDGE_BOTTOM_RIGHT][c.x][c.y] = true;
            EDGE_LISTS[EDGE_BOTTOM_RIGHT][i] = c;
        }
    }

    public static int getEdgeFromStart(Coords start) {
        if (start.x < BOARD_SIZE/2) {
            if(start.y < BOARD_SIZE/2) {
                return EDGE_TOP_RIGHT;
            } else {
                return EDGE_BOTTOM_RIGHT;
            }
        } else {
            if(start.y < BOARD_SIZE/2) {
                return EDGE_TOP_LEFT;
            } else {
                return EDGE_BOTTOM_LEFT;
            }
        }
    }

    /**
     * The valid area in which all units can go during the entire game.
     */
    public static final boolean[][] ARENA;
    static {
        // Superimpose all edges
        ARENA = new boolean[BOARD_SIZE][BOARD_SIZE];
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                for (int k = 0; k < BOARD_SIZE; k++) {
                    ARENA[j][k] |= IS_ON_EDGE[i][j][k];
                }
            }
        }

        // Fill in the area to compute the area of the whole board.
        for (int y = 0; y < BOARD_SIZE; y++) {
            boolean toggled = false;
            for (int x = 0; x < BOARD_SIZE; x++) {
                if (ARENA[x][y]) {
                    if (toggled) {
                        break;
                    } {
                        toggled = true;
                    }
                } else if (toggled) {
                    ARENA[x][y] = true;
                }
            }
        }
    }

    public static boolean inArena(Coords coords) {
        return coords.x >= 0 && coords.y >= 0 && coords.x < BOARD_SIZE && coords.y < BOARD_SIZE && ARENA[coords.x][coords.y];
    }

}
