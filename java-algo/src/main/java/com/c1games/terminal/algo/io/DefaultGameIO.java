package com.c1games.terminal.algo.io;

import com.c1games.terminal.algo.Config;
import com.c1games.terminal.algo.FrameData;
import com.c1games.terminal.algo.GameIO;
import com.c1games.terminal.algo.map.GameState;
import com.c1games.terminal.algo.map.SpawnCommand;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.Gson;

import java.io.IOException;
import java.io.PrintStream;
import java.util.List;

/**
 * The default implementation of game IO which interacts with the game engine through the standard input, output, and error.
 */
public class DefaultGameIO implements GameIO {
    private Config config = null;
    public TerminatedStringReader scanner;
    private FrameData lastFrame;

    private Gson frameDataGson;
    private Gson spawnCommandGson;

    public DefaultGameIO() {
        scanner = new TerminatedStringReader(System.in, '\n');
    }

    @Override
    public Config config() {
        // make sure that the first line is read in and parsed as config.
        if (config == null) {
            String configData;
            try {
                configData = scanner.await();
            } catch (IOException e) {
                throw new IllegalStateException(e);
            }
            config = Config.GSON.fromJson(configData, Config.class);

            // now that we have the config, we can create the GSON instances for the other serializable types.
            UnitTypeAtlas atlas = new UnitTypeAtlas(config);
            frameDataGson = FrameData.gson(atlas);
            spawnCommandGson = SpawnCommand.gson(atlas);
        }
        return config;
    }

    @Override
    public FrameData nextFrameAnyType() {
        // we need to make sure that the first line we read from stdin is the config
        config();
        // then we can read the next frame
        String frameData;
        try {
            frameData = scanner.await();
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
        lastFrame = frameDataGson.fromJson(frameData, FrameData.class);
        return lastFrame;
    }

    @Override
    public FrameData nextTurnFrame() {
        // just get the next frame until one is the action phase
        FrameData frame;
        do {
            frame = nextFrameAnyType();
        } while (frame.turnInfo.phase == FrameData.TurnInfo.Phase.Action);
        return frame;
    }

    @Override
    public GameState nextMoveBuilder() {
        return new GameState(config(), nextTurnFrame());
    }

    @Override
    public FrameData lastFrame() {
        return lastFrame;
    }

    @Override
    public void submitTurn(GameState builder) {
        // serialize and send to stdout
        for (List<SpawnCommand> commands : builder.getSpawnCommands()) {
            String line = spawnCommandGson.toJson(commands);
            System.out.println(line);
        }
    }
}
