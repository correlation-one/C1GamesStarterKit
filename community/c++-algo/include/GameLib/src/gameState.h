/*
Description: Represents the current state of the game.
Last Modified: 09 Apr 2019
Author: Isaac Draper
*/

#ifndef GAME_STATE_H
#define GAME_STATE_H

#include <unordered_map>
#include <algorithm>
#include <iostream>
#include <sstream>
#include <vector>

#include "json11/json11.hpp"
#include "customExceptions.h"
#include "navigation.h"
#include "structs.h"
#include "gameMap.h"
#include "structs.h"
#include "enums.h"
#include "util.h"

namespace terminal {

    using json11::Json;
    using std::string;
    using std::vector;

    /// This represents everything about a current state of the game.
    /// It provides a convienent way to add/remove units and
    /// get information about the opponent.
    class GameState {
    public:
        // Functions
        GameState(Json configuration, Json jsonState);
        void submitTurn() const;

        unsigned int attemptSpawn(UNIT_TYPE unitType, Pos pos, int num = 1);
        unsigned int attemptSpawn(UNIT_TYPE unitType, vector<Pos>& locations, int num = 1);
        unsigned int attemptSpawn(UNIT_TYPE unitType, unsigned int x, unsigned int y, int num = 1);

        unsigned int attemptRemove(Pos pos);
        unsigned int attemptRemove(vector<Pos>& locations);
        unsigned int attemptRemove(unsigned int x, unsigned int y);

        bool canSpawn(UNIT_TYPE unitType, const Pos pos, unsigned int num = 1) const;
        bool canSpawn(UNIT_TYPE unitType, unsigned int x, unsigned int y, unsigned int num = 1) const;

        unsigned int numberAffordable(UNIT_TYPE unitType, const Player& player) const;
        unsigned int numberAffordable(UNIT_TYPE unitType, unsigned int playerIndex = 0) const;

        double projectFutureBits(int turnsInFuture, double currentBits, const Player& player) const;
        double projectFutureBits(int turnsInFuture = 1, double currentBits = -1, unsigned int playerIndex = 0) const;

        double getResource(RESOURCE resourceType, const Player& player) const;
        double getResource(RESOURCE resourceType, unsigned int playerIndex = 0) const;

        double typeCost(UNIT_TYPE unitType) const;
        RESOURCE resourceRequired(UNIT_TYPE unitType) const;

        void findPathToEdge(vector<Pos>& path, Pos startLocation, EDGE targetEdge);
        void findPathToEdge(vector<Pos>& path, unsigned int x, unsigned int y, EDGE targetEdge);

        bool isStationary(UNIT_TYPE unitType) const;
        Player getPlayer(int id) const;
        unsigned int getTurn() const;

        void setVerbosity(VERBOSITY newErrorLevel);
        void suppressWarnings();

        virtual string toString() const;

        // Members
        GameMap gameMap;            ///< Holds the game map associated with this state.

    private:
        // Functions
        void parseState(Json jsonState);
        void parseUnits(Player& player, Json::array jsonUnits);
        void parsePlayerStats(Player& player, unsigned int id, Json::array stats);

        void setResource(RESOURCE resourceType, double amount, Player& player);
        void setResource(RESOURCE resourceType, double amount, unsigned int playerIndex = 0);

        // Members
        Json config;                ///< Holds information about the game.

        Player player1;             ///< Holds stats for the first player.
        Player player2;             ///< Holds stats for the second player.

        Json::array buildStack;     ///< The static units we will send to the engine to spawn.
        Json::array deployStack;    ///< The mobile units we will send to the engine to spawn.

        unsigned int turnNumber;    ///< The current turn number.
        VERBOSITY verbosity;        ///< The level at which to print and throw errors.
    };

    /// This sends a representation of the GameState object to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, GameState const& gameState) {
        os << gameState.toString();
        return os;
    }

}

#endif