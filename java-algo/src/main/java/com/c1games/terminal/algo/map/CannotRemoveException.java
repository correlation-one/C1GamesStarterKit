package com.c1games.terminal.algo.map;

/**
 * Exception thrown when a move builder is used to attempt to remove a structrue, which cannot be removed.
 */
public class CannotRemoveException extends RuntimeException {
    public final CanRemove reasonCannotRemove;

    public CannotRemoveException(CanRemove reasonCannotRemove) {
        this.reasonCannotRemove = reasonCannotRemove;
    }

    @Override
    public String toString() {
        return reasonCannotRemove.toString();
    }
}
