/*
Description: A header to contain the core components necessary for an algo.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#ifndef ALGO_CORE_H
#define ALGO_CORE_H

#include <string>

#include "json11/json11.hpp"
#include "customExceptions.h"
#include "utilities.h"

namespace terminal {

    using json11::Json;

    class AlgoCore {
    public:
        AlgoCore();
        void onGameStart(Json configuration);
        void onTurn(Json gameState);
        void submitDefaultTurn();
        void start();

    private:
        Json config;
        bool endOfGame;

    };

}

#endif
