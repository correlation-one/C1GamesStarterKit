/*
Description: This is a header for GameUnits
Last Modified: 07 Apr 2019
Author: Ryan Draves
*/

#ifndef UNIT_H
#define UNIT_H

#include <iostream>
#include <string>
#include "enums.h"
#include "customExceptions.h"

#include "json11/json11.hpp"

namespace terminal {

    using std::string;
    using json11::Json;

    /// Static function regarding whether a game unit is stationary
    /// @param unitType Unit type to check
    /// @return boolean result of if the unit is stationary
    static bool isStationary(const UNIT_TYPE &unitType) {
        if (unitType == FILTER ||
            unitType == ENCRYPTOR ||
            unitType == DESTRUCTOR)
                return true;
        return false;
    }

    /// Static function to get the string shorthand of a game unit
    /// @param unitType unit type to check
    /// @return string shorthand of the unit, used for print outs
    static string unitTypeStr(const UNIT_TYPE &unitType) {
        switch (unitType) {
            case FILTER:
                return "FF";
                break;
            case ENCRYPTOR:
                return "EF";
                break;
            case DESTRUCTOR:
                return "DF";
                break;
            case PING:
                return "PI";
                break;
            case EMP:
                return "EI";
                break;
            case SCRAMBLER:
                return "SI";
                break;
            case REMOVE:
                return "RM";
                break;
            default:
                throw UnitTypeException();
        }
        throw UnitTypeException();
        return "";
    }

    /// A class to represent game units
    class GameUnit {
        /*Holds information about a Unit. 

        Attributes:
            * unitType (UNIT_TYPE): This unit's type
            * config (Json): Contains information about the game
            * playerIndex (integer): The player that controls this unit. 0 for you, 1 for your opponent.
            * x (integer): The x coordinate of the unit
            * y (integer): The y coordinate of the unit
            * stationary (bool): Whether or not this unit is a firewall
            * speed (double): A unit will move once every 1/speed frames
            * damage (int): The amount of damage this firwall unit will deal to enemy information.
            * damageF (int): The amount of damage this information unit will deal to enemy firewalls.
            * damageI (int): The amount of damage this information unit will deal to enemy information.
            * range (double): The effective range of this unit
            * max_stability (double): The starting stability of this unit. Note than stability can be increased beyond this value by encryptors
            * stability (double): The current health of this unit
            * cost (int): The resource cost of this unit

        */
    public:
        GameUnit(UNIT_TYPE unitType, const Json &config, double stability, int playerIndex = 0,
            int x = -1, int y = -1);
        string toString() const;
        string str() { return toString(); };
        string repr() { return toString(); };
    private:
        void serializeType();
    public:
        // To be initialized
        UNIT_TYPE unitType;
        Json config;
        int playerIndex;
        double stability;
        int x;
        int y;
        // To be read in by config
        bool stationary;
        double speed;
        int damage;
        int damageF;
        int damageI;
        double range;
        double maxStability;
        int cost;
        bool pendingRemoval;
    };

    /// This sends a representation of the GameUnit object to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, GameUnit const& gameUnit) {
        os << gameUnit.toString();
        return os;
    }

}


#endif
