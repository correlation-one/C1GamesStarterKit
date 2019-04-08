/*
Description: Implmentations for the unit.h header.
Last Modified: 07 Apr 2019
Author: Ryan Draves
*/

#include "unit.h"

namespace terminal {
    
    using std::string;
    using std::to_string;
    using std::stoi;
    using std::stof;
    using json11::Json;
    typedef enum UNIT_TYPE UnitType;

    // Init the passed in params and pass off config initialization to serialize_type()
    GameUnit::GameUnit(UnitType unit_type, const Json &config, float stability, int player_index,
        int x, int y) : unit_type(unit_type), config(config), player_index(player_index),
        stability(stability), x(x), y(y), pending_removal(false) {
        serialize_type();
    }

    // Finish the game unit initialization based on the config
    void GameUnit::serialize_type() {
        stationary = is_stationary(unit_type);
        Json type_config = config["unitInformation"][(int)unit_type];
        if (stationary) {
            speed = 0;
            if (unit_type == REMOVE) {
                pending_removal = true;
                // Initialize these in case someone decides to access them...
                damage = damage_f = damage_i = max_stability = range = cost = 0;
                return;
            }
            else if (unit_type == ENCRYPTOR) {
                damage = stoi(type_config["shieldAmount"].string_value());
            }
            else {
                damage = stoi(type_config["damage"].string_value());
            }
            damage_f = damage;
            damage_i = damage;
        }
        else {
            speed = stof(type_config["speed"].string_value());
            damage_f = stoi(type_config["damageF"].string_value());
            damage_i = stoi(type_config["damageI"].string_value());
        }
        range = stof(type_config["range"].string_value());
        max_stability = stof(type_config["stability"].string_value());
        cost = stoi(type_config["cost"].string_value());
    }

    // Get a string representation of the game unit
    string GameUnit::toString() {
        string owner = player_index == 0 ? "Friendly" : "Enemy";
        string removal = pending_removal ? ", pending removal" : "";
        return owner + " " + unit_type_str(unit_type) + ", stability: " +
            to_string(stability) + " location: [" + to_string(x) + ", " +
            to_string(y) + "]" + removal;
    }
}
