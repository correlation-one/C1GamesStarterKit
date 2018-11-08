package com.c1games.terminal.algo.map;

import com.c1games.terminal.algo.serialization.JsonSerializeClassToTuple;
import com.c1games.terminal.algo.serialization.UnitTypeSerializer;
import com.c1games.terminal.algo.units.UnitType;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

/**
 * The GSON-serializable representation of the spawn commands which are sent in a list to the game engine at the end of a turn.
 */
public class SpawnCommand {
    public UnitType type;
    public int x;
    public int y;

    public SpawnCommand(UnitType type, int x, int y) {
        this.type = type;
        this.x = x;
        this.y = y;
    }

    /**
     * Produce a gson instance capable of serializing a spawncommand.
     */
    public static Gson gson(UnitTypeAtlas atlas) {
        return new GsonBuilder()
                .registerTypeAdapter(UnitType.class, new UnitTypeSerializer(atlas))
                .registerTypeAdapter(SpawnCommand.class, new JsonSerializeClassToTuple<>(SpawnCommand.class))
                .create();
    }
}
