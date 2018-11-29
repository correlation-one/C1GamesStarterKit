package test;

import com.c1games.terminal.algo.serialization.JsonDeserializeClassFromTuple;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.junit.Test;


public class JsonDeserializeClassFromTupleTest {
    public static final class Example {
        public int foo;
        public transient long transientExample = 394;
        public String bar;
        public static String staticExample = "bonjour";
        public float baz;

        @Override
        public String toString() {
            return "Example{" +
                    "foo=" + foo +
                    ", transientExample=" + transientExample +
                    ", bar='" + bar + '\'' +
                    ", baz=" + baz +
                    '}';
        }
    }

    @Test public void test() {
        Gson gson = new GsonBuilder()
                .registerTypeAdapter(Example.class, new JsonDeserializeClassFromTuple<Example>(Example.class, Example::new))
                .create();
        String serialized = "[42, \"hello world\", 3.14]";
        Example example = gson.fromJson(serialized, Example.class);

        System.out.println(example);

        assert example.foo == 42;
        assert example.transientExample == 394;
        assert example.bar.equals("hello world");
        assert Example.staticExample.equals("bonjour");
        assert example.baz == 3.14f;
    }
}
