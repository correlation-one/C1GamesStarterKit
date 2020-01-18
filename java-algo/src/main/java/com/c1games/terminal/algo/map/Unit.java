package com.c1games.terminal.algo.map;

import com.c1games.terminal.algo.Config;
import com.c1games.terminal.algo.PlayerId;
import com.c1games.terminal.algo.units.UnitType;

/**
 * A unit which is at a certain position on the map.
 */
public class Unit {
    public final UnitType type;
    public final float health;
    public final String id;
    public final PlayerId owner;
    public final Config.UnitInformation unitInformation;
    public boolean removing = false;
    public boolean upgraded = false;

    public Unit(UnitType type, float health, String id, PlayerId owner, Config config) {
        unitInformation = new Config.UnitInformation(config.unitInformation.get(type.ordinal()));
        this.type = type;
        this.health = health;
        this.id = id;
        this.owner = owner;
    }

    public void upgrade() {
        upgraded = true;
        unitInformation.upgrade();
    }
}
