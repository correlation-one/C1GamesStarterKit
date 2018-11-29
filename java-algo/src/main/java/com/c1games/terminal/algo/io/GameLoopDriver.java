package com.c1games.terminal.algo.io;

import com.c1games.terminal.algo.Config;
import com.c1games.terminal.algo.FrameData;
import com.c1games.terminal.algo.GameIO;
import com.c1games.terminal.algo.map.GameState;

/**
 * Code that accepts some @code GameLoop object and runs it for the duration of the game.
 */
public class GameLoopDriver implements Runnable {
    private final GameLoop loop;

    public GameLoopDriver(GameLoop loop) {
        this.loop = loop;
    }

    @Override
    public void run() {
        GameIO io = new DefaultGameIO();

        // wait for config, invoke config handler
        Config config = io.config();
        loop.initialize(io, config);

        while (true) {
            FrameData frame = io.nextFrameAnyType();
            if (frame.turnInfo.phase == FrameData.TurnInfo.Phase.Action) {
                // invoke action frame handler
                GameState move = new GameState(config, frame);
                loop.onActionFrame(io, move);
            } else if (frame.turnInfo.phase == FrameData.TurnInfo.Phase.Deploy) {
                // invoke the move handler and then submit the move builder
                GameState move = new GameState(config, frame);
                loop.onTurn(io, move);
                io.submitTurn(move);
            } else {
                // game over, exit
                return;
            }
        }
    }
}
