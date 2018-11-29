package com.c1games.terminal.algo.serialization;

import com.c1games.terminal.algo.units.FirewallUnitType;
import com.c1games.terminal.algo.units.UnitType;
import com.c1games.terminal.algo.units.UnitTypeAtlas;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;

import java.lang.reflect.Type;

/**
 * GSON deserializer for firewall unit types from their shorthand strings as defined in the config.
 */
public class FirewallUnitTypeDeserializer implements JsonDeserializer<FirewallUnitType> {
    private final UnitTypeAtlas atlas;

    public FirewallUnitTypeDeserializer(UnitTypeAtlas atlas) {
        this.atlas = atlas;
    }

    @Override
    public FirewallUnitType deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        try {
            UnitType unitType = jsonDeserializationContext.deserialize(jsonElement, UnitType.class);
            return unitType.toFirewall();
        } catch (Exception e) {
            throw new JsonParseException(e);
        }
    }
}
