/*
Description: This is a header for GameUnits
Last Modified: 07 Apr 2019
Author: Ryan Draves
*/

#ifndef UNIT_H
#define UNIT_H

#include <string>
#include "enums.h"
#include "customExceptions.h"

#include "json11/json11.hpp"

namespace terminal {

    using std::string;
    using json11::Json;
    typedef enum UNIT_TYPE UnitType;

    // Static function regarding whether a game unit is stationary
    static bool is_stationary(const UnitType &unit_type) {
        if (unit_type == FILTER ||
            unit_type == ENCRYPTOR ||
            unit_type == DESTRUCTOR)
                return true;
        return false;
    }

    // Static function to get the string shorthand of a game unit
    static string unit_type_str(const UnitType &unit_type) {
        switch (unit_type) {
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
                return "RF";
                break;
            default:
                throw UnitTypeException();
        }
        throw UnitTypeException();
        return "";
    }

    // A class to represent game units
    class GameUnit {
        /*Holds information about a Unit. 

        Attributes:
            * unit_type (enemy UNIT_TYPE): This unit's type
            * config (Json): Contains information about the game
            * player_index (integer): The player that controls this unit. 0 for you, 1 for your opponent.
            * x (integer): The x coordinate of the unit
            * y (integer): The y coordinate of the unit
            * stationary (bool): Whether or not this unit is a firewall
            * speed (float): A unit will move once every 1/speed frames
            * damage (int): The amount of damage this firwall unit will deal to enemy information.
            * damage_f (int): The amount of damage this information unit will deal to enemy firewalls.
            * damage_i (int): The amount of damage this information unit will deal to enemy information.
            * range (float): The effective range of this unit
            * max_stability (float): The starting stability of this unit. Note than stability can be increased beyond this value by encryptors
            * stability (float): The current health of this unit
            * cost (int): The resource cost of this unit

        */
    public:
        GameUnit(UnitType unit_type, const Json &config, float stability, int player_index = 0,
            int x = -1, int y = -1);
        string toString();
        string str() { return toString(); };
        string repr() { return toString(); };
    private:
        void serialize_type();
    public:
        // To be initialized
        UnitType unit_type;
        Json config;
        int player_index;
        float stability;
        int x;
        int y;
        // To be read in by config
        bool stationary;
        int speed;
        int damage;
        int damage_f;
        int damage_i;
        float range;
        float max_stability;
        int cost;
        bool pending_removal;
    };

}


#endif