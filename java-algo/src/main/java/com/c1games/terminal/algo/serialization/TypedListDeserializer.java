package com.c1games.terminal.algo.serialization;

import com.google.gson.*;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

/**
 * GSON deserializer for a class which is represented by another list of elements. This particular deserializer is able to be aware of the type
 * of the elements of the list, and thus dispatch a customized deserializer for the list elements. This is, unfortunately, not possible in
 * regular java due to type erasure within java generics.
 */
public class TypedListDeserializer<L, E> implements JsonDeserializer<L> {
    private final Function<List<E>, L> factory;
    private final Class<E> elementClass;

    public TypedListDeserializer(Function<List<E>, L> factory, Class<E> elementClass) {
        this.factory = factory;
        this.elementClass = elementClass;
    }

    @Override
    public L deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) throws JsonParseException {
        try {
            JsonArray array = json.getAsJsonArray();
            List<E> elements = new ArrayList<>();
            for (JsonElement jsonElement : array) {
                E element = context.deserialize(jsonElement, elementClass);
                elements.add(element);
            }
            return factory.apply(elements);
        } catch (Exception e) {
            throw new JsonParseException(e);
        }
    }
}
