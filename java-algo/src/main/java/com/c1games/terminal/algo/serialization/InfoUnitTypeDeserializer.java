package com.c1games.terminal.algo.serialization;

import com.c1games.terminal.algo.units.InfoUnitType;
import com.c1games.terminal.algo.units.UnitType;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;

import java.lang.reflect.Type;

/**
 * GSON deserializer for info unit types from their shorthand strings as defined in the config.
 */
public class InfoUnitTypeDeserializer implements JsonDeserializer<InfoUnitType> {
    private final UnitTypeAtlas atlas;

    public InfoUnitTypeDeserializer(UnitTypeAtlas atlas) {
        this.atlas = atlas;
    }

    @Override
    public InfoUnitType deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        try {
            UnitType unitType = jsonDeserializationContext.deserialize(jsonElement, UnitType.class);
            return unitType.toInfo();
        } catch (Exception e) {
            throw new JsonParseException(e);
        }
    }
}
