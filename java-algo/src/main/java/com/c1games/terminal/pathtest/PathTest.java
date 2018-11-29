package com.c1games.terminal.pathtest;

import com.c1games.terminal.algo.Coords;
import com.c1games.terminal.algo.io.DefaultGameIO;
import com.c1games.terminal.algo.map.GameState;
import com.c1games.terminal.algo.serialization.JsonDeserializeClassFromTuple;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.*;
import java.util.List;
import java.util.stream.Collectors;

public class PathTest {
    public static void main(String[] args) throws IOException {
        DefaultGameIO io = new DefaultGameIO();
        while (true) {
            GameState move = io.nextMoveBuilder();
            Gson gson = new GsonBuilder()
                    .registerTypeAdapter(Coords.class, new JsonDeserializeClassFromTuple<>(Coords.class, () -> new Coords(0, 0)))
                    .create();
            Coords start = gson.fromJson(io.scanner.await(), Coords.class);
            int direction = Integer.parseInt(io.scanner.await());
            List<Coords> pathAsCoords = move.pathfind(start, direction);
            List<List<Integer>> pathAsLists = pathAsCoords.stream()
                    .map(c -> List.of(c.x, c.y))
                    .collect(Collectors.toList());
            String pathAsString = gson.toJson(pathAsLists);
            System.out.println(pathAsString);
        }
    }
}
