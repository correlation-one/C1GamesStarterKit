/*
Description: Implementations for the gameState header.
Last Modified: 10 Apr 2019
Author: Isaac Draper
*/

#include "gameState.h"

namespace terminal {

    using json11::Json;
    using std::to_string;
    using std::string;
    using std::vector;

    /// Constructor for GameState which requires a configuration Json object
    /// and a Json object representing the current state of the game.
    /// @param configuration A Json object containing information about the game.
    /// @param currentState A Json object containing information about the current state.
    GameState::GameState(Json configuration, Json jsonState) : gameMap(configuration) {
        config = configuration;
        verbosity = WARNING;

        buildStack = Json::array();
        deployStack = Json::array();

        parseState(jsonState);
    }

    /// Fills in the rest of the required data from the engine.
    /// Converts the Json object into data to be used by the class members.
    /// @param jsonState A Json object containing the current state of the game.
    void GameState::parseState(Json jsonState) {
        turnNumber = jsonState["turnInfo"].array_items().at(1).int_value();

        Json::array p1Stats = jsonState["p1Stats"].array_items();
        Json::array p2Stats = jsonState["p2Stats"].array_items();

        parsePlayerStats(player1, 0, p1Stats);
        parsePlayerStats(player2, 1, p2Stats);

        Json::array p1Units = jsonState["p1Units"].array_items();
        Json::array p2Units = jsonState["p2Units"].array_items();

        parseUnits(player1, p1Units);
        parseUnits(player2, p2Units);
    }

    /// Fills in the appropriate information for a player by reference.
    /// @param player The player to parse the stats for (by reference).
    /// @param stats A Json array containing the stats for the player.
    void GameState::parsePlayerStats(Player& player, unsigned int id, Json::array stats) {
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

                UNIT_TYPE unitType = static_cast<UNIT_TYPE>(i);
                unsigned int x = unitRaw.at(0).int_value();
                unsigned int y = unitRaw.at(1).int_value();
                double hp = unitRaw.at(2).number_value();

                gameMap.addUnit(unitType, x, y, player.id, hp);
            }
            ++i;
        }
    }

    /// Sets a resource for a player. This is called internally.
    /// @param resourceType The resource type to set.
    /// @param amount The new amount to set.
    /// @param player The player whos resource to update.
    void GameState::setResource(RESOURCE resourceType, double amount, Player& player) {
        double heldResource = getResource(resourceType, player);
        if (resourceType == BITS) {
            player.bits = heldResource + amount;
        }
        else if (resourceType == CORES) {
            player.cores = heldResource + amount;
        }
    }

    /// Sets a resource for a player. This is called internally.
    /// The default player is player 1.
    /// @param resourceType The resource type to set.
    /// @param amount The new amount to set.
    /// @param playerIndex The id of the player to get (0 or 1).
    void GameState::setResource(RESOURCE resourceType, double amount, unsigned int playerIndex) {
        playerIndex == 0 ?
            setResource(resourceType, amount, player1) :
            setResource(resourceType, amount, player2);
    }

    /// Gets the amount of a resource held by a player.
    /// @param resourceType The resource type to get.
    /// @param player The player whos resource to get.
    /// @return The amount of a resouce a player has.
    double GameState::getResource(RESOURCE resourceType, const Player& player) const {
        return resourceType == BITS ? player.bits : player.cores;
    }

    /// Gets the amount of a resource held by a player.
    /// The default is player 1.
    /// @param resourceType The resource type to get.
    /// @param playerIndex The player whos resource to get.
    /// @return The amount of a resouce player1 has.
    double GameState::getResource(RESOURCE resourceType, unsigned int playerIndex) const {
        return playerIndex == 0 ?
            getResource(resourceType, player1) :
            getResource(resourceType, player2);
    }

    /// Returns the type of resource required to build a unit
    /// based on the unit type passed.
    /// @param unitType the UNIT_TYPE to get the resource.
    /// @return The type of resource the given unit requires.
    RESOURCE GameState::resourceRequired(UNIT_TYPE unitType) const {
        return isStationary(unitType) ? CORES : BITS;
    }

    /// Submits and ends your turn, sending all changes to the engine.
    /// Must be called at the end of your turn.
    /// This should be called only once per turn.
    void GameState::submitTurn() const {
        Util::sendCommand(Json(buildStack).dump());
        Util::sendCommand(Json(deployStack).dump());
    }

    /// Checks if a unit type is stationary.
    /// @param unitType The unit type to check.
    /// @return A bool saying whether it is stationary.
    bool GameState::isStationary(UNIT_TYPE unitType) const {
        return unitType < 3;
    }

    /// Returns a player struct based on the player number passed.
    /// @param id The player number.
    /// @return A player struct containing information about the player.
    Player GameState::getPlayer(int id) const {
        return id == 1 ? player1 : player2;
    }

    /// Returns the current turn number of the game.
    /// @return The current turn number.
    unsigned int GameState::getTurn() const {
        return turnNumber;
    }

    /// The number of units a player can afford.
    /// @param unitType The type of unit to check.
    /// @param player The player to use.
    /// @return The number of units that player can afford.
    unsigned int GameState::numberAffordable(UNIT_TYPE unitType, const Player& player) const {
        double cost = typeCost(unitType);
        RESOURCE resourceType = resourceRequired(unitType);
        double playerHeld = getResource(resourceType, player);

        return (unsigned int)(playerHeld / cost);
    }

    /// The number of units a player can afford.
    /// @param unitType The type of unit to check.
    /// @param playerIndex The player to use (0 or 1).
    /// @return The number of units that player can afford.
    unsigned int GameState::numberAffordable(UNIT_TYPE unitType, unsigned int playerIndex) const {
        return playerIndex == 0 ?
            numberAffordable(unitType, player1) :
            numberAffordable(unitType, player2);
    }

    /// Predicts the number of bits a player will have in a future turn.
    /// @param turnsInFuture The number of turns to look ahead.
    /// @param currentBits Will use this value instead of player's if passed.
    /// @param player The player to use.
    /// @return The number of bits after so many turns.
    double GameState::projectFutureBits(int turnsInFuture, double currentBits, const Player& player) const {
        if (turnsInFuture < 1 || turnsInFuture > 99) {
            Util::printError<CustomException>("Invalid turns in future used (" + std::to_string(turnsInFuture) + "). Turns in future should be betweeen 1 and 99.", WARNING, verbosity);
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
    /// @param currentBits Will use this value instead of player's if passed.
    /// @param playerIndex The player to use.
    /// @return The number of bits after so many turns.
    double GameState::projectFutureBits(int turnsInFuture, double currentBits, unsigned int playerIndex) const {
        return playerIndex == 0 ?
            projectFutureBits(turnsInFuture, currentBits, player1) :
            projectFutureBits(turnsInFuture, currentBits, player2);
    }

    /// Gets the cost of a unit based on it's type.
    /// @param unitType The type of unit.
    /// @return The cost of the unit.
    double GameState::typeCost(UNIT_TYPE unitType) const {
        return config["unitInformation"].array_items().at(unitType)["cost"].number_value();
    }

    /// Checks if we can spawn a unit at a given location.
    /// @param unitType The type of unit to check.
    /// @param x The x position to check.
    /// @param y The y position to check.
    /// @param num The number of units to check, default is 1.
    /// @return A bool, true if can spawn.
    bool GameState::canSpawn(UNIT_TYPE unitType, unsigned int x, unsigned int y, unsigned int num) const {
        if (!gameMap.inArenaBounds(x, y)) {
            Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
            return false;
        }

        const bool affordable = numberAffordable(unitType, player1) >= num;
        const bool stationary = isStationary(unitType);
        const bool blocked = gameMap.containsStationaryUnit(x, y) ||
            (stationary && gameMap[Pos(x, y)].size() > 0);
        const bool correctTerritory = y < gameMap.HALF_ARENA;

        vector<Pos> edges;
        gameMap.getEdgeLocations(edges, BOTTOM_LEFT);
        gameMap.getEdgeLocations(edges, BOTTOM_RIGHT);
        const bool onEdge = std::find(edges.begin(), edges.end(), Pos(x, y)) != edges.end();

        string failReason = "";
        if (!affordable)
            failReason += " Not enough resources.";
        if (blocked)
            failReason += " Location is blocked.";
        if (!correctTerritory)
            failReason += " Location in enemy territory.";
        if (!(stationary || onEdge))
            failReason += " Information units must be deployed on the edge.";
        if (failReason.length() > 0)
            Util::printError<UnitSpawnException>("Could not spawn " +
                unitTypeStr(unitType) + " at location " +
                "(" + to_string(x) + ", " + to_string(y) + "). " +
                failReason, 
                WARNING, verbosity);

        return (affordable && correctTerritory && !blocked && (stationary || onEdge) && (!stationary || num == 1));
    }

    /// Checks if we can spawn a unit at a given location.
    /// @param unitType The type of unit to check.
    /// @param pos The position to check.
    /// @param num The number of units to check, default is 1.
    /// @return A bool, true if can spawn.
    bool GameState::canSpawn(UNIT_TYPE unitType, Pos pos, unsigned int num) const {
        return canSpawn(unitType, pos.x, pos.y, num);
    }

    /// Attempts to spawn new units with the type give at a single location.
    /// @param unitType The type of unit to spawn.
    /// @param x The x location to spawn the unit.
    /// @param y The y location to spawn the unit.
    /// @param num The number of units to spawn.
    /// @return Returns the number of units spawned (0 or 1).
    unsigned int GameState::attemptSpawn(UNIT_TYPE unitType, unsigned int x, unsigned int y, int num) {
        if (canSpawn(unitType, x, y)) {
            int cost = (int)typeCost(unitType);
            RESOURCE resourceType = resourceRequired(unitType);
            setResource(resourceType, 0 - cost);

            gameMap.addUnit(unitType, x, y, 0);

            if (isStationary(unitType))
                buildStack.push_back({ Json::array({ unitTypeStr(unitType), (int)x, (int)y }) });
            else
                deployStack.push_back({ Json::array({ unitTypeStr(unitType), (int)x, (int)y }) });

            return 1;
        }
        else {
            Util::printError<UnitSpawnException>("Tried to spawn unit at (" + to_string(x) + ", " + to_string(y) + ") but could not.", WARNING, verbosity);
        }

        return 0;
    }

    /// Attempts to spawn new units with the type give at a single location.
    /// @param unitType The type of unit to spawn.
    /// @param pos The location to spawn the unit.
    /// @param num The number of units to spawn.
    /// @return Returns the number of units spawned (0 or 1).
    unsigned int GameState::attemptSpawn(UNIT_TYPE unitType, Pos pos, int num) {
        return attemptSpawn(unitType, pos.x, pos.y);
    }

    /// Attempts to spawn units with the type give at a list of locations.
    /// @param unitType The type of unit to spawn.
    /// @param locations A vector of locations to spawn the units.
    /// @param num The numer of units to spawn at each location (default is 1).
    /// @return Returns the number of units spawned.
    unsigned int GameState::attemptSpawn(UNIT_TYPE unitType, vector<Pos>& locations, int num) {
        if (num < 1) {
            Util::printError<UnitSpawnException>("Attempted to spawn fewer than one unit.", WARNING, verbosity);
        }

        unsigned int numSpawned = 0;
        for (Pos pos : locations) {
            numSpawned += attemptSpawn(unitType, pos);
        }

        return numSpawned;
    }

    /// Attempts to remove existing friendly firewalls in a given location.
    /// @param x The x location to try and remove.
    /// @param y The y location to try and remove.
    /// @return Returns the number of units removed (0 or 1).
    unsigned int GameState::attemptRemove(unsigned int x, unsigned int y) {
        if (y < gameMap.HALF_ARENA &&
            gameMap.containsStationaryUnit(Pos(x, y))) {
            buildStack.push_back({ Json::array({ unitTypeStr(REMOVE), (int)x, (int)y}) });

            return 1;
        }
        else {
            Util::printError<UnitRemoveException>("Could not remove a unit from (" + to_string(x) + ", " + to_string(y) + "). Location has no firewall or it is in enemy territory", WARNING, verbosity);
        }

        return 0;
    }

    /// Attempts to remove existing friendly firewalls in a given location.
    /// @param pos The location to try and remove.
    /// @return Returns the number of units removed (0 or 1).
    unsigned int GameState::attemptRemove(Pos pos) {
        return attemptRemove(pos.x, pos.y);
    }

    /// Attempts to remove existing friendly firewalls at each position in a vector.
    /// @param locations The locations to try and remove.
    /// @return Returns the number of units removed.
    unsigned int GameState::attemptRemove(vector<Pos>& locations) {
        unsigned int numRemoved = 0;
        for (Pos pos : locations) {
            numRemoved += attemptRemove(pos);
        }

        return numRemoved;
    }

    /// Sets a new verbosity level. This determines whether errors will
    /// be ignored, printed, or throw exceptions.
    /// This also sets the verbosity of the GameMap.
    /// @param newVerbosity The new error level.
    void GameState::setVerbosity(VERBOSITY newVerbosity) {
        verbosity = newVerbosity;
        gameMap.setVerbosity(newVerbosity);
    }

    /// Sets the verbosity level to SUPPRESS.
    /// This causes all errors to be ignored.
    /// This also sets the verbosity of the GameMap.
    void GameState::suppressWarnings() {
        verbosity = SUPPRESS;
        gameMap.setVerbosity(SUPPRESS);
    }

    /// This returns a string representation of the GameState object.
    /// @return A string to represent this object.
    string GameState::toString() const {
        std::stringstream ss;
        ss.precision(1);
        ss << std::fixed;

        ss << "GameState:\n\t\t\tBits\tCores\tHealth\n\t" <<
            "Player 1:\t" <<
            player1.bits  << "\t" <<
            player1.cores << "\t" <<
            player1.health << "\n\t" <<
            "Player 2:\t" <<
            player2.bits  << "\t" <<
            player2.cores << "\t" <<
            player2.health << "\n";

        return ss.str();
    }

}
