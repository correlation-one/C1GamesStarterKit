package com.c1games.terminal.algo.serialization;

import com.c1games.terminal.algo.units.UnitType;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.JsonElement;
import com.google.gson.JsonPrimitive;
import com.google.gson.JsonSerializationContext;
import com.google.gson.JsonSerializer;

import java.lang.reflect.Type;

/**
 * GSON serializer for unit types to their shorthand strings as defined in the config.
 */
public class UnitTypeSerializer implements JsonSerializer<UnitType> {
    private final UnitTypeAtlas atlas;

    public UnitTypeSerializer(UnitTypeAtlas atlas) {
        this.atlas = atlas;
    }

    @Override
    public JsonElement serialize(UnitType src, Type typeOfSrc, JsonSerializationContext context) {
        return new JsonPrimitive(atlas.getString(src));
    }
}
