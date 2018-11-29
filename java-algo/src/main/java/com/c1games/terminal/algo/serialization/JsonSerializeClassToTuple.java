package com.c1games.terminal.algo.serialization;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonSerializationContext;
import com.google.gson.JsonSerializer;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;

/**
 * GSON deserializer that deserializes a class into an array, serializing each the value of each field, in order, into that corresponding
 * index in the array. Ignores static, final, and transient fields.
 */
public class JsonSerializeClassToTuple<T> implements JsonSerializer<T> {
    private final Class<T> typeClass;

    public JsonSerializeClassToTuple(Class<T> typeClass) {
        this.typeClass = typeClass;
    }

    @Override
    public JsonElement serialize(T src, Type typeOfSrc, JsonSerializationContext context) {
        try {
            JsonArray array = new JsonArray();
            for (Field field : typeClass.getFields()) {
                if ((field.getModifiers() & Modifier.STATIC) != 0)
                    continue;
                if ((field.getModifiers() & Modifier.TRANSIENT) != 0)
                    continue;
                if ((field.getModifiers() & Modifier.FINAL) != 0)
                    continue;

                Object value = field.get(src);
                array.add(context.serialize(value));
            }
            return array;
        } catch (Exception e) {
            throw new RuntimeException("serialize class to tuple exception: ", e);
        }
    }
}
