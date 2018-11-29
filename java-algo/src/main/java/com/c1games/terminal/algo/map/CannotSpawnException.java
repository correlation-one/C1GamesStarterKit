package com.c1games.terminal.algo.map;

/**
 * Exception thrown when a move builder is used to attempt to spawn a unit, which cannot be spawned.
 */
public class CannotSpawnException extends RuntimeException {
    public final CanSpawn reasonCannotSpawn;

    public CannotSpawnException(CanSpawn reasonCannotSpawn) {
        this.reasonCannotSpawn = reasonCannotSpawn;
    }

    @Override
    public String toString() {
        return reasonCannotSpawn.toString();
    }
}
