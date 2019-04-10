/*
Description: A header for the current game state of the class.
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
        GameState(Json configuration, Json jsonState);
        void submitTurn() const;

        int numberAffordable(UNIT_TYPE unitType) const;
        int numberAffordable(UNIT_TYPE unitType, const Player& player) const;

        bool canSpawn(UNIT_TYPE unitType, int x, int y, int num = 1) const;
        bool canSpawn(UNIT_TYPE unitType, const Pos pos, int num = 1) const;

        int attemptSpawn(UNIT_TYPE unitType, int x, int y, int num = 1);
        int attemptSpawn(UNIT_TYPE unitType, Pos pos, int num = 1);
        int attemptSpawn(UNIT_TYPE unitType, vector<Pos> locations, int num = 1);

        int attemptRemove(Pos pos);
        int attemptRemove(int x, int y);
        int attemptRemove(vector<Pos> locations);

        double projectFutureBits(int turnsInFuture = 1, double currentBits = -1) const;
        double projectFutureBits(int turnsInFuture, double currentBits, const Player& player) const;

        double typeCost(UNIT_TYPE unitType) const;
        RESOURCE resourceRequired(UNIT_TYPE unitType) const;
        double getResource(RESOURCE resourceType) const;
        double getResource(RESOURCE resourceType, const Player& player) const;
        bool isStationary(UNIT_TYPE unitType) const;
        Player getPlayer(int id) const;
        int getTurn() const;

        void setVerbosity(VERBOSITY newErrorLevel);
        void suppressWarnings();

        virtual string toString() const;

        // public members
        GameMap gameMap;

    private:
        void parseState(Json jsonState);
        void parsePlayerStats(Player& player, int id, Json::array stats);
        void parseUnits(Player& player, Json::array jsonUnits);

        void setResource(RESOURCE resourceType, double amount);
        void setResource(RESOURCE resourceType, double amount, Player& player);

        Json config;
        Player player1;
        Player player2;
        Json::array buildStack;
        Json::array deployStack;
        int turnNumber;
        GameMap gameMap;
        VERBOSITY errorLevel;
        GameMap gameMap;
        // TODO: Add pathfinding

    };

    /// This sends a representation of the GameState object to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, GameState const& gameState) {
        os << gameState.toString();
        return os;
    }

}

#endif