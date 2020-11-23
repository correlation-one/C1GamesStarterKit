package com.c1games.terminal.algo.map;

/**
 * The result of querying whether a structure can be removed at a particular location, 
 * denoting either that it can be removed, or the reason
 * why it cannot.
 */
public enum CanRemove {
    Yes,
    OutOfBounds,
    WrongSideOfMap,
    NoUnitPresent,
    InfoUnitPresent,
    ;

    public boolean affirmative() {
        return this == CanRemove.Yes;
    }
}
