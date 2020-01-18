package com.c1games.terminal.algo;

import com.c1games.terminal.algo.map.GameState;

import java.io.PrintStream;

/**
 * Input and output with the game engine.
 *
 * This object is used for logging messages, receiving configs and frame data, and making moves.
 *
 * This object, in many ways, functions similarly to an iterator of frame data, received from the game engine via the standard input.
 *
 * This object is not at all guaranteed to be thread safe.
 */
public interface GameIO {
    /**
     * A printstream to log data which will become visible to the client/user.
     */
    static PrintStream debug() {
        return System.err;
    };

    /**
     * Get the deserialized config file, possibly waiting to receive this from the game. This many block initially, since the game needs time to
     * send over the config file, but will only block once, for the same reason.
     */
    Config config();

    /**
     * Waits for the next frame from the engine of the Action phase, which corresponds to the beginning of the turn. This will skip over any frames
     * which are not of that type.
     *
     * Nullable.
     */
    FrameData nextTurnFrame();

    /**
     * Wait for the next turn frame, and then use it to construct a move builder.
     */
    GameState nextMoveBuilder();

    /**
     * Wait for the next frame data from the engine for any type. There are several frames per turn. Many algos will prefer to call nextTurnFrame.
     *
     * Nullable
     */
    FrameData nextFrameAnyType();

    /**
     * Get the last frame returned by nextTurnFrame or nextFrameAnyType.
     *
     * Nullable.
     */
    FrameData lastFrame();

    /**
     * Given a set of moves created by a move buider, submit those to the engine as our actions for this turn.
     */
    void submitTurn(GameState builder);
}
