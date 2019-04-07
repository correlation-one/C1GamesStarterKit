/*
Description: A header for the current game state of the class.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#ifndef GAME_STATE_H
#define GAME_STATE_H

#include <unordered_map>

#include "json11/json11.hpp"
#include "GameLib/src/structs.h"
#include "GameLib/src/enums.h"
#include "GameLib/src/util.h"

namespace terminal {

    using json11::Json;
    using std::string;

    /// This represents everything about a current state of the game.
    /// It provides a convienent way to add/remove units and
    /// get information about the opponent.
    class GameState {
    public:
        GameState(Json configuration, Json jsonState);

    private:
        void parseState(Json jsonState);
        void parsePlayerStats(Player& player, int id, Json::array stats);
        void parseUnits(Player& player, Json::array jsonUnits);
        Unit createUnit(Player& player, int uType, Json::array unitRaw);

        Json config;
        Player player1;
        Player player2;
        Json buildStack;
        Json deployStack;
        int turnNumber;
        // TODO: Add GameMap
        // TODO: Add pathfinding

        std::unordered_map<UNIT_TYPE, string> unitStr;

    };

}

#endif