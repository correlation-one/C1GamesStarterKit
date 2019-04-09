/*
Description: A header to contain the components and logic of one's strategy.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#ifndef ALGO_STRATEGY_H
#define ALGO_STRATEGY_H

#include <unordered_map>
#include <vector>

#include "json11/json11.hpp"
#include "GameLib/src/gameState.h"
#include "GameLib/src/algoCore.h"
#include "GameLib/src/structs.h"
#include "GameLib/src/enums.h"
#include "GameLib/src/util.h"

namespace terminal {

    using json11::Json;

    /// This class will contain most of the logic and be what you edit the most.
    /// You should start this class and override the functions defined in
    /// AlgoCore in order to define your own strategy.
    class AlgoStrategy : public terminal::AlgoCore {
    public:
        AlgoStrategy();

    private:
        void onGameStart(Json configuration) override;
        void onTurn(Json jsonState) override;
        void starterStrategy(GameState& gameState);
        void buildC1Logo(GameState& gameState);
        void buildDefences(GameState& gameState);
        void deployAttackers(GameState& gameState);
        vector<Pos> filterBlockedLocations(vector<Pos>& locations, GameState& gameState);
        
    };

}

#endif
