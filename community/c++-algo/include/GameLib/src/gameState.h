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

#include "json11/json11.hpp"
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
        double getResource(RESOURCE rType);
        double getResource(RESOURCE rType, Player& player);
        double projectFutureBits(int turnsInFuture = 1, double currentBits = -1);
        double projectFutureBits(int turnsInFuture, double currentBits, Player& player);
        int numberAffordable(UNIT_TYPE uType);
        int numberAffordable(UNIT_TYPE uType, Player& player);
        bool canSpawn(UNIT_TYPE uType, Pos pos, int num = 1);
        int attemptSpawn(UNIT_TYPE uType, Pos pos);
        int attemptSpawn(UNIT_TYPE uType, vector<Pos> locations, int num = 1);
        int attemptRemove(Pos pos);
        int attemptRemove(vector<Pos> locations);
        Player getPlayer(int id);
        void submitTurn();
        virtual string toString() const;

    private:
        void parseState(Json jsonState);
        void parsePlayerStats(Player& player, int id, Json::array stats);
        void parseUnits(Player& player, Json::array jsonUnits);

        void setResource(RESOURCE rType, double amount);
        void setResource(RESOURCE rType, double amount, Player& player);
        RESOURCE resourceRequired(UNIT_TYPE uType);
        double typeCost(UNIT_TYPE uType);
        bool isStationary(UNIT_TYPE uType);

        Json config;
        Player player1;
        Player player2;
        Json::array buildStack;
        Json::array deployStack;
        int turnNumber;
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