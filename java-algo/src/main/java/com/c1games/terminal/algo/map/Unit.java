package com.c1games.terminal.algo.map;

import com.c1games.terminal.algo.PlayerId;
import com.c1games.terminal.algo.units.UnitType;

/**
 * A unit which is at a certain position on the map.
 */
public class Unit {
    public final UnitType type;
    public final float stability;
    public final String id;
    public final PlayerId owner;

    public Unit(UnitType type, float stability, String id, PlayerId owner) {
        this.type = type;
        this.stability = stability;
        this.id = id;
        this.owner = owner;
    }
}
