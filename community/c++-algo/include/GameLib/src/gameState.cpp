/*
Description: Implementations for the gameState header.
Last Modified: 08 Apr 2019
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

                // TODO: Create a unit from the raw data using Unit class (not merged yet)
                // TODO: Add the unit to the GameMap
            }
            ++i;
        }
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

    /// Gets the amount of a resource held by a player.
    /// @param rType The resource type to get.
    /// @return The amount of a resouce player1 has.
    double GameState::getResource(RESOURCE rType) {
        return getResource(rType, player1);
    }

    /// Returns the type of resource based on the unit type.
    /// @param uType the UNIT_TYPE to get the resource.
    /// @return The type of resource the given unit requires.
    RESOURCE GameState::resourceRequired(UNIT_TYPE uType) {
        return isStationary(uType) ? CORES : BITS;
    }

    /// Submits and ends your turn, sending all changes to the engine.
    /// Must be called at the end of your turn.
    void GameState::submitTurn() {
        Util::sendCommand(Json(buildStack).dump());
        Util::sendCommand(Json(deployStack).dump());
    }

    /// Checks if a unit type is stationary.
    /// @param uType The unit type to check.
    /// @return A bool saying whether it is stationary
    bool GameState::isStationary(UNIT_TYPE uType) {
        return uType < 3;
    }

    Player GameState::getPlayer(int id) {
        return id == 1 ? player1 : player2;
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

    /// The number of units a player can afford.
    /// @param uType The type of unit to check.
    /// @return The number of units that player can afford.
    int GameState::numberAffordable(UNIT_TYPE uType) {
        return numberAffordable(uType, player1);
    }

    /// Predicts the number of bits a player will have in a future turn.
    /// @param turnsInFuture The number of turns to look ahead.
    /// @param currentBits Will use this value instead of player's if passed. Also if it is negative.
    /// @param player The player to use.
    /// @return The number of bits after so many turns.
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
            bits = ((int)(bits * 100 + 0.5)) / 100.0;
        }

        return bits;
    }
    
    /// Predicts the number of bits a player will have in a future turn.
    /// @param turnsInFuture The number of turns to look ahead.
    /// @param currentBits Will use this value instead of player's if passed. Also if it is negative.
    /// @return The number of bits after so many turns.
    double GameState::projectFutureBits(int turnsInFuture, double currentBits) {
        return projectFutureBits(turnsInFuture, currentBits, player1);
    }


    /// Gets the cost of a unit based on it's type.
    /// @param uType The type of unit.
    /// @return The cost of the unit.
    double GameState::typeCost(UNIT_TYPE uType) {
        return config["unitInformation"].array_items().at(uType)["cost"].number_value();
    }

    /// Checks if we can spawn a unit at a given location.
    /// @param uType The type of unit to check.
    /// @param pos The position to check.
    /// @param num The number of units to check, default is 1.
    /// @return A bool, true if can spawn.
    bool GameState::canSpawn(UNIT_TYPE uType, Pos pos, int num) {
        // TODO: Add inside map check here.

        int affordable = numberAffordable(uType, player1);
        bool stationary = isStationary(uType);

        // TODO: Add map

        return false;
    }

}
