package com.c1games.terminal.algo.serialization;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;

import java.lang.reflect.Type;

/**
 * GSON deserializer which deserializes an enum from an integer, simply producing the variant of the enum with the index that corresponds to
 * the JSON iterator.
 */
public class JsonDeserializeEnumFromInt<T> implements JsonDeserializer<T> {
    private final Class<T> typeClass;
    private int offset;

    public JsonDeserializeEnumFromInt(Class<T> typeClass) {
        this.typeClass = typeClass;
        StartIndexAt[] startIndexAt = typeClass.getAnnotationsByType(StartIndexAt.class);
        if (startIndexAt.length > 0)
            offset = startIndexAt[0].value();
        else
            offset = 0;
    }

    @Override
    public T deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        try {
            return typeClass.getEnumConstants()[jsonElement.getAsInt() - offset];
        } catch (Exception e) {
            throw new JsonParseException(e);
        }
    }
}
