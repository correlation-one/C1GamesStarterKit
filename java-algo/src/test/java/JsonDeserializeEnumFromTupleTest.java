package test;

import com.c1games.terminal.algo.serialization.JsonDeserializeEnumFromInt;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.junit.Test;

public class JsonDeserializeEnumFromTupleTest {
    public enum Foo {
        Zero,
        One,
        Two
    }

    @Test public void test() {
        Gson gson = new GsonBuilder()
                .registerTypeAdapter(Foo.class, new JsonDeserializeEnumFromInt<Foo>(Foo.class))
                .create();
        assert gson.fromJson("0", Foo.class) == Foo.Zero;
        assert gson.fromJson("1", Foo.class) == Foo.One;
        assert gson.fromJson("2", Foo.class) == Foo.Two;
    }
}
