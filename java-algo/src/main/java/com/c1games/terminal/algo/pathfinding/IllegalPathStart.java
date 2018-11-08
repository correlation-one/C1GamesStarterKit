package com.c1games.terminal.algo.pathfinding;

/**
 * A reason why pathfinding from a particular tile is illegal, used by the IllegalPathStart exception.s
 */
public enum IllegalPathStart {
    BlockedByWall,
    OutsideOfArena,
}
