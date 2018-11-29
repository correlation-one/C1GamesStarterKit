package com.c1games.terminal.algo.serialization;

import com.google.gson.*;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;
import java.util.function.Supplier;

/**
 * GSON deserializer that deserializes a class from an array, deserializing each the value of each field, in order, from that corresponding
 * index in the array. Ignores static, final, and transient fields.
 */
public class JsonDeserializeClassFromTuple<T> implements JsonDeserializer<T> {
    private final Class<T> typeClass;
    private final Supplier<T> typeFactory;

    public JsonDeserializeClassFromTuple(Class<T> typeClass, Supplier<T> typeFactory) {
        this.typeClass = typeClass;
        this.typeFactory = typeFactory;
    }

    @Override
    public T deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        try {
            JsonArray jsonArray = jsonElement.getAsJsonArray();

            T instance = typeFactory.get();

            Field[] typeFields = typeClass.getFields();
            int tupleIndex = 0;
            for (int i = 0; i < typeFields.length; i++) {
                Field field = typeFields[i];

                if ((field.getModifiers() & Modifier.STATIC) != 0)
                    continue;
                if ((field.getModifiers() & Modifier.TRANSIENT) != 0)
                    continue;
                if ((field.getModifiers() & Modifier.FINAL) != 0)
                    continue;

                Class<?> fieldClass = field.getType();
                Object fieldValue = jsonDeserializationContext.deserialize(jsonArray.get(tupleIndex), fieldClass);
                field.set(instance, fieldValue);

                tupleIndex++;
            }

            return instance;
        } catch (Exception e) {
            throw new JsonParseException(e);
        }
    }
}
