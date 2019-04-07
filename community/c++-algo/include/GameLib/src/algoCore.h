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

    /// This is the super class to contain the basic essentials.
    /// You should inherit from this class when developing your strategy.
    class AlgoCore {
    public:
        AlgoCore();
        virtual void start();

    protected:
        virtual void onGameStart(Json configuration);
        virtual void onTurn(Json gameState);
        void submitDefaultTurn() const;

        Json config;

    private:
        bool endOfGame;

    };

}

#endif
