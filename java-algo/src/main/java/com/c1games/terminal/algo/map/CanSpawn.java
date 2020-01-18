package com.c1games.terminal.algo.map;

/**
 * The result of querying whether a unit can be spawned at a particular location, denoting either that it can be spawned, or the reason
 * why it cannot.
 */
public enum CanSpawn {
    Yes,
    OutOfBounds,
    WrongSideOfMap,
    NotOnEdge,
    NotEnoughResources,
    UnitAlreadyPresent,
    NoUnitPresent,
    ;

    public boolean affirmative() {
        return this == CanSpawn.Yes;
    }
}
