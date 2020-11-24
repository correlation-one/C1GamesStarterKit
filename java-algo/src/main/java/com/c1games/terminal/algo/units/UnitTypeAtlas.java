package com.c1games.terminal.algo.units;

import com.c1games.terminal.algo.Config;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Lookup between java-represented unit types and string representations, as denoted in the config file.
 */
public class UnitTypeAtlas {
    private final Map<UnitType, String> byUnitType;
    private final Map<String, UnitType> toUnitType;

    public UnitTypeAtlas(Config config) {
        byUnitType = new HashMap<>();
        byUnitType.put(UnitType.Wall, config.unitInformation.get(0).getShorthand());
        byUnitType.put(UnitType.Support, config.unitInformation.get(1).getShorthand());
        byUnitType.put(UnitType.Turret, config.unitInformation.get(2).getShorthand());
        byUnitType.put(UnitType.Scout, config.unitInformation.get(3).getShorthand());
        byUnitType.put(UnitType.Demolisher, config.unitInformation.get(4).getShorthand());
        byUnitType.put(UnitType.Interceptor, config.unitInformation.get(5).getShorthand());
        byUnitType.put(UnitType.Remove, config.unitInformation.get(6).getShorthand());
        byUnitType.put(UnitType.Upgrade, config.unitInformation.get(7).getShorthand());
        toUnitType = byUnitType
                .entrySet()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));
    }

    public String getString(UnitType type) {
        return byUnitType.get(type);
    }

    public UnitType getUnitType(String string) {
        return toUnitType.get(string);
    }
}
