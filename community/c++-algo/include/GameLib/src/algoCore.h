/*
Description: This contains the core components necessary for an algo to run.
Last Modified: 08 Apr 2019
Author: Isaac Draper
*/

#ifndef ALGO_CORE_H
#define ALGO_CORE_H

#include <iostream>
#include <string>

#include "json11/json11.hpp"
#include "customExceptions.h"
#include "util.h"

namespace terminal {

    using json11::Json;

    /// This is the super class to contain the basic essentials.
    /// You should inherit from this class when developing your strategy.
    class AlgoCore {
    public:
        // Functions
        AlgoCore();
        virtual void start();
        virtual std::string toString() const;

    protected:
        // Functions
        virtual void onGameStart(Json configuration);
        virtual void onTurn(Json gameState);
        void submitDefaultTurn() const;

        // Members
        Json config; ///< Holds information about the game.

    private:
        // Members
        bool endOfGame; ///< Keeps track of whether the game has ended.

    };

    /// This sends a representation of the AlgoCore object to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, AlgoCore const& algoCore) {
        os << algoCore.toString();
        return os;
    }

}

#endif
