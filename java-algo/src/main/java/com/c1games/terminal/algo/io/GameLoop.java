package com.c1games.terminal.algo.io;

import com.c1games.terminal.algo.Config;
import com.c1games.terminal.algo.GameIO;
import com.c1games.terminal.algo.map.GameState;

/**
 * An interface for a simple, single-threaded game loop, which the user can implement and then plug into a
 * game loop driver to create a working algo.
 */
public interface GameLoop {
    /**
     * Callback for receiving the config data at the beginning of the game. Not all algos will have a reason
     * to process this.
     */
    default void initialize(GameIO io, Config config) {}

    /**
     * Callback for processing an action frame data received between deploy phases. Not all algos will have a reason
     * to process this. This move builder is only used for random access to the map, and will not actually be
     * submitted.
     */
    default void onActionFrame(GameIO io, GameState move) {}

    /**
     * Callback for configuring a movebuilder each action frame, which the game loop driver will then submit as
     * a turn.
     */
    void onTurn(GameIO io, GameState move);
}
