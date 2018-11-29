package com.c1games.terminal.algo.pathfinding;

public class IllegalPathStartException extends RuntimeException {
    public final IllegalPathStart reason;

    public IllegalPathStartException(IllegalPathStart reason) {
        this.reason = reason;
    }

    @Override
    public String toString() {
        return "IllegalPathStartException{" +
                "reason=" + reason +
                '}';
    }
}
