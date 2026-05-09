/*
Description: Holds the representation of a GameUnit.
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

    /// Static function to say whether a unit type is stationary.
    /// @param unitType Unit type to check.
    /// @return boolean Whether the unit type is stationary.
    static bool isStationary(const UNIT_TYPE &unitType) {
        if (unitType == FILTER ||
            unitType == ENCRYPTOR ||
            unitType == DESTRUCTOR)
                return true;
        return false;
    }

    /// Static function to get the string shorthand of a game unit.
    /// @param unitType Unit type to check.
    /// @return string Shorthand of the unit in string form.
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

    /// A class to represent a unit from terminal.
    /// This keeps track of that units health, type,
    /// etc as given by the engine.
    class GameUnit {
    public:
        // Functions
        GameUnit(UNIT_TYPE unitType, const Json &config, double stability, int playerIndex = 0,
            int x = -1, int y = -1);
        string toString() const;

        // Members
        Json config;                ///< Holds information about the game.

        UNIT_TYPE unitType;         ///< The type of this unit.
        int playerIndex;            ///< Which player it belongs to.
        double stability;           ///< The health of this unit.
        int x;                      ///< The x position of its location.
        int y;                      ///< The y position of its location.

        // Determines these members from the config.
        bool stationary;            ///< Whether the unit is a firewall.
        double speed;               ///< How often this unit moves (0 if static).
        int damage;                 ///< The amount of damage this unit does.
        int damageF;                ///< The damage done to firewalls.
        int damageI;                ///< The damage done to information units.
        double range;               ///< How far away this unit can attack.
        double maxStability;        ///< The maximum amound of health it can have.
        int cost;                   ///< How much it costs to spawn.
        bool pendingRemoval;        ///< If it has been attempted to be removed.

    private:
        // Functions
        void serializeType();

    };

    /// This sends a representation of the GameUnit object to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, GameUnit const& gameUnit) {
        os << gameUnit.toString();
        return os;
    }

}


#endif
