/*
Description: Implementations for the gameState header.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#include "gameState.h"

namespace terminal {

    using json11::Json;

    /// Constructor for GameState which requires a configuration Json object
    /// and a Json object representing the current state of the game.
    /// @param configuration A Json object containing information about the game.
    /// @param currentState A Json object containing information about the current state.
    GameState::GameState(Json configuration, Json jsonState) {
        config = configuration;

        for (int i = 0; i < 7; ++i) {
            unitStr[static_cast<UNIT_TYPE>(i)] =
                config["unitInformation"].array_items().at(i)["shorthand"].string_value();
        }

        buildStack = Json::array();
        deployStack = Json::array();

        parseState(jsonState);
    }

    /// Fill in the rest of the required data from the engine.
    /// Converts the Json object into data to be used by the class members.
    void GameState::parseState(Json jsonState) {
        turnNumber = jsonState["turnInfo"].array_items().at(1).int_value();

        Json::array p1Stats = jsonState["p1Stats"].array_items();
        Json::array p2Stats = jsonState["p2Stats"].array_items();

        parsePlayerStats(player1, 1, p1Stats);
        parsePlayerStats(player2, 2, p2Stats);

        Json::array p1Units = jsonState["p1Units"].array_items();
        Json::array p2Units = jsonState["p2Units"].array_items();

        parseUnits(player1, p1Units);
        parseUnits(player2, p2Units);
    }

    /// Fills in the appropriate information for a player by reference.
    /// @param player The player to parse the stats for (by reference).
    /// @param stats A Json array containing the stats for the player.
    void GameState::parsePlayerStats(Player& player, int id, Json::array stats) {
        player.health = stats.at(0).int_value();
        player.cores = stats.at(1).number_value();
        player.bits = stats.at(2).number_value();
        player.time = stats.at(3).int_value();
        player.id = id;
    }

    /// Parses Json units and creates unit structs to be used by the GameState.
    /// @param jsonUnits A Json array containing Json arrays of units.
    /// @param player The player the units belong to (by reference).
    void GameState::parseUnits(Player& player, Json::array jsonUnits) {
        int i = 0;
        for (Json unitsObj : jsonUnits) {
            Json::array unitsRaw = unitsObj.array_items();
            for (Json unitObj : unitsRaw) {
                Json::array unitRaw = unitObj.array_items();

                // Create a unit from the raw data
                Unit unit = createUnit(player, i, unitRaw);

                // TODO: Add the unit to the GameMap
            }
            ++i;
        }
    }

    /// Creates a unit struct based on a Json object.
    /// @param player The player the units belong to (by reference).
    /// @param uType The type of unit it is in integer format.
    /// @param unitRaw A Json object containing the information for the current unit.
    /// @return A Unit struct with data filled in from the state and config.
    Unit GameState::createUnit(Player& player, int uType, Json::array unitRaw) {
        // Get the config information for this type of unit
        Json typeConfig = config["unitInformation"].array_items().at(uType);

        UNIT_TYPE unitType = static_cast<UNIT_TYPE>(uType);
        bool stationary = uType < 3;
        double speed;
        double damageStatic;
        double damageMobile;

        if (stationary) {
            speed = 0;
            if (unitType == ENCRYPTOR) {
                damageMobile = typeConfig["shieldAmount"].number_value();
            }
            else {
                damageMobile = typeConfig["damage"].number_value();
            }
            damageStatic = 0;
        }
        else {
            speed = typeConfig["speed"].number_value();
            damageStatic = typeConfig["damageF"].number_value();
            damageMobile = typeConfig["damageI"].number_value();
        }

        double range = typeConfig["range"].number_value();
        double maxHealth = typeConfig["stability"].number_value();
        double cost = typeConfig["cost"].number_value();

        // Create the struct to return.
        Unit unit = {
            unitType,                           // unit type
            player,                             // owner
            Pos {
                unitRaw.at(0).int_value(),      // x position
                unitRaw.at(1).int_value()       // y position
            },
            unitRaw.at(2).number_value(),       // health
            unitRaw.at(3).int_value(),          // unique id
            stationary,                         // is stationary
            speed,                              // speed
            damageStatic,                       // damage done to static units
            damageMobile,                       // damage done to mobile units
            range,                              // attack (or heal) range
            maxHealth,                          // maximum health
            cost                                // cost to build
        };

        return unit;
    }

    /// Sets a resource for a player. This is called internally.
    /// @param rType The resource type to set.
    /// @param amount The new amount to set.
    /// @param player The player whos resource to update.
    void GameState::setResource(RESOURCE rType, double amount, Player& player) {
        double heldResource = getResource(rType, player);
        if (rType == BITS) {
            player.bits = heldResource + amount;
        }
        else if (rType == CORES) {
            player.cores = heldResource + amount;
        }
    }

    /// Gets the amount of a resource held by a player.
    /// @param rType The resource type to get.
    /// @param player The player whos resource to get.
    /// @return The amount of a resouce a player has.
    double GameState::getResource(RESOURCE rType, Player& player) {
        if (rType != BITS && rType != CORES) {
            // TODO: create warn function and warn about unit type
            return -1;
        }

        return rType == BITS ? player.bits : player.cores;
    }

    /// Returns the type of resource based on the unit type.
    /// @param uType the UNIT_TYPE to get the resource.
    /// @return The type of resource the given unit requires.
    RESOURCE GameState::resourceRequired(UNIT_TYPE uType) {
        return uType < 3 ? CORES : BITS;
    }

    /// Submits and ends your turn, sending all changes to the engine.
    /// Must be called at the end of your turn.
    void GameState::submitTurn() {
        Util::sendCommand(Json(buildStack).dump());
        Util::sendCommand(Json(deployStack).dump());
    }

    /// The number of units a player can afford.
    /// @param uType The type of unit to check.
    /// @param player The player to use.
    /// @return The number of units that player can afford.
    int GameState::numberAffordable(UNIT_TYPE uType, Player& player) {
        double cost = typeCost(uType);
        RESOURCE rType = resourceRequired(uType);
        double playerHeld = getResource(rType, player);
        return (int)(playerHeld / cost);
    }

    /// Predicts the number of bits a player will have in a future turn.
    /// @param turnsInFuture The number of turns to look ahead.
    /// @param currentBits Will use this value instead of player's if passed. Also if it is negative.
    /// @param player The player to use.
    double GameState::projectFutureBits(int turnsInFuture, double currentBits, Player& player) {
        if (turnsInFuture < 1 || turnsInFuture > 99) {
            // TODO: Create warning here.
        }

        double bits = currentBits >= 0 ? currentBits : getResource(BITS, player);
        for (int i = 1; i < turnsInFuture + 1; ++i) {
            int currentTurn = turnNumber + i;
            bits *= (1 - config["resources"]["bitDecayPerRound"].number_value());
            double bitsGained = config["resources"]["bitsPerRound"].number_value() + (int)(currentTurn / config["resources"]["turnIntervalForBitSchedule"].number_value());
            bits += bitsGained;
            bits = std::trunc(bits * 10) / 10;
        }

        return bits;
    }

    /// Gets the cost of a unit based on it's type.
    /// @param uType The type of unit.
    /// @return The cost of the unit.
    double GameState::typeCost(UNIT_TYPE uType) {
        return config["unitInformation"].array_items().at(uType)["cost"].number_value();
    }

}
