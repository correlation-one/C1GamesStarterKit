/*
Description: Implmentations for the unit.h header.
Last Modified: 07 Apr 2019
Author: Ryan Draves
*/

#include "unit.h"

namespace terminal {
    
    using std::string;
    using std::to_string;
    using json11::Json;

    /// Init the passed in params and pass off config initialization to serializeType()
    /// @param unitType Unit type of the game unit.
    /// @param config JSON game configuration passed in upon startup.
    /// @param stability Health of the game unit. 0 defaults it to maxStability.
    /// @param playerIndex 0 for ally unit (you), 1 for enemy unit.
    /// @param x X coordinate of the game unit's location.
    /// @param y Y coordinate of the game unit's location.
    GameUnit::GameUnit(UNIT_TYPE unitType, const Json &config, double stability, int playerIndex,
        int x, int y) : unitType(unitType), config(config), playerIndex(playerIndex),
        stability(stability), x(x), y(y), pendingRemoval(false) {
        serializeType();
        this->stability = stability == 0 ? maxStability : stability;
    }

    /// Finish the game unit initialization based on the config
    void GameUnit::serializeType() {
        stationary = isStationary(unitType);
        Json type_config = config["unitInformation"].array_items().at((int)unitType);
        if (stationary) {
            speed = 0;
            if (unitType == REMOVE) {
                pendingRemoval = true;
                // Initialize these in case someone decides to access them...
                damage = damageF = damageI = maxStability = range = cost = 0;
                return;
            }
            else if (unitType == ENCRYPTOR) {
                damage = type_config["shieldAmount"].int_value();
            }
            else {
                damage = type_config["damage"].int_value();
            }
            damageF = damage;
            damageI = damage;
        }
        else {
            speed = type_config["speed"].number_value();
            damageF = type_config["damageF"].int_value();
            damageI = type_config["damageI"].int_value();
        }
        range = type_config["range"].number_value();
        maxStability = type_config["stability"].number_value();
        cost = type_config["cost"].int_value();
    }

    /// Get a string representation of the game unit
    /// @return Elegant string representation of the game unit
    string GameUnit::toString() const {
        string owner = playerIndex == 0 ? "Friendly" : "Enemy";
        string removal = pendingRemoval ? ", pending removal" : "";
        return owner + " " + unitTypeStr(unitType) + ", stability: " +
            to_string(stability) + " location: [" + to_string(x) + ", " +
            to_string(y) + "]" + removal;
    }
}
