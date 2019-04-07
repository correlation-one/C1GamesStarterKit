/*
Description: Implementations for the algoStrategy header.
Last Modified: 07 Apr 2019
Author: Isaac Draper
*/

#include "algoStrategy.h"

namespace terminal {

    using json11::Json;
    using std::string;

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

    /// A function that runs at the start of every game.
    /// This is overridden from AlgoCore to perform initial setup
    /// at the start of the game, based on the configuration.
    /// @param configuration A Json object containing information about the game.
    void AlgoStrategy::onGameStart(Json configuration) {
        Util::debugWrite("Configuring your custom algo strategy...");
        config = configuration;
    }

    /// Called when the engine expects input from the algo.
    /// It is called every turn and is passed a Json object containing
    /// the current game state, which can be used to initialize a new gameState.
    /// This is overridden from AlgoCore.
    /// @param jsonState A Json object containing the current game state.
    void AlgoStrategy::onTurn(Json jsonState) {
        GameState gameState = GameState(config, jsonState);
        gameState.submitTurn();
    }

}
