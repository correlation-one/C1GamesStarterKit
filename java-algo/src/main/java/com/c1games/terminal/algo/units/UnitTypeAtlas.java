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
    private final Map<InfoUnitType, String> byInfoUnitType;
    private final Map<FirewallUnitType, String> byFirewallUnitType;
    public final String remove;
    private final Map<String, UnitType> toUnitType;
    private final Map<String, InfoUnitType> toInfoUnitType;
    private final Map<String, FirewallUnitType> toFirewallUnitType;

    public UnitTypeAtlas(Config config) {
        byUnitType = new HashMap<>();
        byUnitType.put(UnitType.Filter, config.unitInformation.get(0).getShorthand());
        byUnitType.put(UnitType.Encryptor, config.unitInformation.get(1).getShorthand());
        byUnitType.put(UnitType.Destructor, config.unitInformation.get(2).getShorthand());
        byUnitType.put(UnitType.Ping, config.unitInformation.get(3).getShorthand());
        byUnitType.put(UnitType.EMP, config.unitInformation.get(4).getShorthand());
        byUnitType.put(UnitType.Scrambler, config.unitInformation.get(5).getShorthand());
        byUnitType.put(UnitType.Remove, config.unitInformation.get(6).getShorthand());
        toUnitType = byUnitType
                .entrySet()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));

        byFirewallUnitType = new HashMap<>();
        byFirewallUnitType.put(FirewallUnitType.Filter, config.unitInformation.get(0).getShorthand());
        byFirewallUnitType.put(FirewallUnitType.Encryptor, config.unitInformation.get(1).getShorthand());
        byFirewallUnitType.put(FirewallUnitType.Destructor, config.unitInformation.get(2).getShorthand());
        toFirewallUnitType = byFirewallUnitType
                .entrySet()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));

        byInfoUnitType = new HashMap<>();
        byInfoUnitType.put(InfoUnitType.Ping, config.unitInformation.get(3).getShorthand());
        byInfoUnitType.put(InfoUnitType.EMP, config.unitInformation.get(4).getShorthand());
        byInfoUnitType.put(InfoUnitType.Scrambler, config.unitInformation.get(5).getShorthand());
        toInfoUnitType = byInfoUnitType
                .entrySet()
                .stream()
                .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));

        remove = config.unitInformation.get(6).getShorthand();
    }

    public String getString(UnitType type) {
        return byUnitType.get(type);
    }

    public String getString(InfoUnitType type) {
        return byInfoUnitType.get(type);
    }

    public String getString(FirewallUnitType type) {
        return byFirewallUnitType.get(type);
    }

    public UnitType getUnitType(String string) {
        return toUnitType.get(string);
    }

    public InfoUnitType getInfoUnitType(String string) {
        return toInfoUnitType.get(string);
    }

    public FirewallUnitType getFirewallUnitType(String string) {
        return toFirewallUnitType.get(string);
    }
}
