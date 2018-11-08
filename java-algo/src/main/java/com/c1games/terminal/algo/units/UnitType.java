package com.c1games.terminal.algo.units;

import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.Scanner;

public enum UnitType {
    Filter,
    Encryptor,
    Destructor,
    Ping,
    EMP,
    Scrambler,
    Remove
    ;

    public boolean isFirewall() {
        return this == Filter || this == Encryptor || this == Destructor;
    }

    public boolean isInfo() {
        return this == Ping || this == EMP || this == Scrambler;
    }

    public FirewallUnitType toFirewall() throws NoSuchElementException {
        if (this == Filter) {
            return FirewallUnitType.Filter;
        } else if (this == Encryptor) {
            return FirewallUnitType.Encryptor;
        } else if (this == Destructor) {
            return FirewallUnitType.Destructor;
        } else {
            throw new NoSuchElementException(this + " is not a firewall");
        }
    }

    public InfoUnitType toInfo() throws  NoSuchElementException {
        if (this == Ping) {
            return InfoUnitType.Ping;
        } else if (this == EMP) {
            return InfoUnitType.EMP;
        } else if (this == Scrambler) {
            return InfoUnitType.Scrambler;
        } else {
            throw new NoSuchElementException(this + " is not an info");
        }
    }
}
