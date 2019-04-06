/*
Description: Implementations for the algoStrategy header.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#include "algoStrategy.h"

namespace terminal {

    /*
        Most of the algo code you write will be in this file unless you create new
        modules yourself. Start by modifying the 'on_turn' function.

        Advanced strategy tips :
            Additional functions are made available by importing the AdvancedGameState
            class from gamelib / advanced.py as a replacement for the regular GameState class in game.py.

        You can analyze action frames by modifying algoCore.h/cpp.

        The GameState.map object can be manually manipulated to create hypothetical
        board states.Though, it is recommended to make a copy of the map to preserve
        the actual current map state.
    */

    /// Basic constructor for algoCore which calls it's superclass, AlgoCore.
    AlgoStrategy::AlgoStrategy() : AlgoCore::AlgoCore() {
    
    }

}
