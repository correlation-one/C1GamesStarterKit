/*
Description: Implementations for the algoCore header.
Last Modified: 06 Apr 2019
Author: Isaac Draper
*/

#include "algoCore.h"

namespace terminal {

    using json11::Json;

    /// Basic constructor for algoCore.
    AlgoCore::AlgoCore() {
        std::string error;
        config = Json::parse("{}", error);
        endOfGame = false;
    }

    /// A function that runs at the start of every game.
    /// Override this to perform initial setup at the start of the game, based on the configuration.
    /// @param configuration A Json object containing information about the game.
    void AlgoCore::onGameStart(Json configuration) {
        config = configuration;
    }

    /// Called when the engine expects input from the algo.
    /// It is called every turn and is passed a Json object containing
    /// the current game state, which can be used to initialize a new gameState.
    /// @param gameState A Json object containing the current game state.
    void AlgoCore::onTurn(Json gameState) {
        AlgoCore::submitDefaultTurn();
    }

    /// Submits a turn that does nothing.
    void AlgoCore::submitDefaultTurn() const {
        Util::sendCommand("[]");
        Util::sendCommand("[]");
    }

    /// Starts the main loop of the program.
    /// This will continue until it gets the end of state signal from the engine.
    /// If there is some error, it will never exit since it will continue
    /// to wait until it recieves input from the engine.
    /// If this happens it must be killed manually.
    void AlgoCore::start() {
        Util::debugWrite("Starting C++ Starter Algo");

        while (true) {
            try {
                Json gameState = Util::getCommand();

                if (gameState["turnInfo"] == nullptr) {
                    // Here we know it is the first turn, and the gameState object
                    // is information about the game, not an actual game state.
                    // Thus, we run the setup for the game.
                    
                    onGameStart(gameState);
                }
                else if (gameState["turnInfo"] != nullptr) {
                    int stateType = gameState["turnInfo"].array_items().at(0).int_value();

                    // We now make decisions based on what turn state it is.
                    switch (stateType) {
                        case 0: {
                            // This is when the engine expects to recieve what we are
                            // building for this turn.
                            // So we run the onTurn function.

                            onTurn(gameState);
                            break;
                        }
                        case 1: {
                            // This is a single frame from the engine.
                            // If you want to get information from the game every frame,
                            // you can create function to do that here.

                            break;
                        }
                        case 2: {
                            // This indicates that the game has ended.
                            // Since break simply takes us out of the switch,
                            // we use a variable to quite the while loop.

                            Util::debugWrite("GOT END OF STATE");
                            endOfGame = true;
                            break;
                        }
                        default: {
                            // This means we got an unexpected string.
                            // This technically should never happen since it would
                            // be caught by the Json parser.

                            Util::debugWrite("Unexpected state recieved: " + stateType);
                            break;
                        }
                    }

                    if (endOfGame) {
                        break;
                    }
                }
            }
            catch (UtilException e) {
                Util::debugWrite(e.what());
                continue;
            }
        }
    }

}
