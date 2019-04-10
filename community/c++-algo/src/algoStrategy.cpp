/*
Description: Implementations for the algoStrategy header.
Last Modified: 09 Apr 2019
Author: Isaac Draper
*/

#include "algoStrategy.h"

namespace terminal {

    using json11::Json;
    using std::string;
    using std::vector;

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
        // Create a gamestate object that will help execute our strategy.
        GameState gameState = GameState(config, jsonState);

        // Print so we know we started our strategy.
        Util::debugWrite("Performing turn ", false);
        Util::debugWrite(gameState.getTurn(), false);
        Util::debugWrite(" of your C++ starter strategy");

        // Run our strategy.
        starterStrategy(gameState);

        // Submit our turn to the engine.
        gameState.submitTurn();
    }

    /*
        NOTE: All the methods after this point are part of the sample starter - algo
        strategy and can safely be replaced for your custom algo.
    */

    /// This starts using the gameState to run our strategy.
    /// @param gameState The current game state of the board (by reference).
    void AlgoStrategy::starterStrategy(GameState& gameState) {
        // Builds the C1 Logo.
        // Calling this first prioritizes repairing the logo before all else.
        buildC1Logo(gameState);

        // Then build additional defences.
        buildDefences(gameState);

        // Finally deploy our information units to attack.
        deployAttackers(gameState);
    }

    /// Here we make the C1 logo.
    /// We use Filter firewalls because they are cheap.
    /// @param gameState The current game state of the board (by reference).
    void AlgoStrategy::buildC1Logo(GameState& gameState) {
        // Build the letter C. 
        vector<Pos> letterC = { Pos {8, 11}, Pos {9, 11}, Pos {7, 10}, Pos {7, 9}, Pos {7, 8}, Pos {8, 7}, Pos {9, 7} };
        for (Pos pos : letterC)
            if (gameState.canSpawn(FILTER, pos))
                gameState.attemptSpawn(FILTER, pos);

        // Build the number 1.
        vector<Pos> number1 = { Pos {17, 11}, Pos {18, 11}, Pos {18, 10}, Pos {18, 9}, Pos {18, 8}, Pos {17, 7}, Pos {18, 7}, Pos {19, 7} };
        for (Pos pos : number1)
            if (gameState.canSpawn(FILTER, pos))
                gameState.attemptSpawn(FILTER, pos);

        // Build the 3 dots with destructors.
        vector<Pos> dots = { Pos {11, 7}, Pos {13, 9}, Pos {15, 11} };
        for (Pos pos : dots)
            if (gameState.canSpawn(DESTRUCTOR, pos))
                gameState.attemptSpawn(DESTRUCTOR, pos);
    }

    /// Builds some extra defences.
    /// @param gameState The current game state of the board (by reference).
    void AlgoStrategy::buildDefences(GameState& gameState) {
        // First we protect ourselves with some destructors.
        vector<Pos> destructorLocations = { Pos {0, 13}, Pos {27, 13} };
        for (Pos pos : destructorLocations)
            if (gameState.canSpawn(DESTRUCTOR, pos))
                gameState.attemptSpawn(DESTRUCTOR, pos);

        // Then lets boost our offense by building some encryptors to shield 
        // our information units.Lets put them near the front because the
        // shields decay over time, so shields closer to the action
        // are more effective.
        vector<Pos> encryptorLocations = { Pos {3, 11}, Pos {4, 11}, Pos {5, 11} };
        for (Pos pos : encryptorLocations)
            if (gameState.canSpawn(ENCRYPTOR, pos))
                gameState.attemptSpawn(ENCRYPTOR, pos);

        // Lastly lets build encryptors in random locations.Normally building
        // randomly is a bad idea but we'll leave it to you to figure out better strategies.
        //
        // First we get all locations on the bottom half of the map
        // that are in the arena bounds.
        vector<Pos> allLocations;
        for (int i = 0; i < gameState.gameMap.ARENA_SIZE; ++i) {
            for (int j = 0; j < gameState.gameMap.HALF_ARENA; ++j) {
                if (gameState.gameMap.inArenaBounds(i, j)) {
                    allLocations.push_back(Pos{ i, j });
                }
            }
        }

        // Then we remove loactions already occupied.
        vector<Pos> possibleLocations = filterBlockedLocations(allLocations, gameState);

        // While we have cores to spend, build random Encryptors.
        while (gameState.getResource(CORES) >= gameState.typeCost(ENCRYPTOR) && !possibleLocations.empty()) {
            // Choose a random location.
            int randomIndex = rand() % possibleLocations.size();
            Pos buildLocation = possibleLocations.at(randomIndex);


            // Build at that location and remove it from our vector.
            gameState.attemptSpawn(ENCRYPTOR, buildLocation);
            possibleLocations.erase(possibleLocations.begin() + randomIndex);
        }
    }

    /// Deploys attackers to the edges of the map.
    /// @param gameState The current game state of the board (by reference).
    void AlgoStrategy::deployAttackers(GameState& gameState) {
        // First lets check if we have 10 bits, if we don't lets
        // wait for a turn that we do.
        if (gameState.getResource(BITS) < 10)
            return;

        // Lets deploy an EMP long range unit to destry firewalls.
        if (gameState.canSpawn(EMP, 3, 10))
            gameState.attemptSpawn(EMP, 3, 10);

        // Now lets send out 3 pings to try and score.
        // We can spawn multiple at the same locatoin.
        if (gameState.canSpawn(PING, 3, 10, 3))
            gameState.attemptSpawn(PING, 3, 10, 3);

        // NOTE: the locations we used above to spawn information units may become
        // blocked by our own firewalls. We'll leave it to you to fix that issue yourselves.
        //
        // Lastly lets send out Scramblers to help destroy enemy information units.
        // A complex algo would predict where the enemy is going to send units and
        // develop its strategy around that. But this algo is simple so lets just
        // send out scramblers in random locations and hope for the best.

        // Firstly, information units can only deploy on our edges.
        // So lets get a list of those locations.
        vector<Pos> friendlyEdges;
        gameState.gameMap.getEdgeLocations(friendlyEdges, BOTTOM_LEFT);
        gameState.gameMap.getEdgeLocations(friendlyEdges, BOTTOM_RIGHT);

        // Remove locations blocked by our own firewalls.
        vector<Pos> deployLocations = filterBlockedLocations(friendlyEdges, gameState);

        // While we have bits to spend, build encryptors randomly.
        while (gameState.getResource(BITS) >= gameState.typeCost(SCRAMBLER) && !deployLocations.empty()) {
            // Choose a random location.
            int randomIndex = rand() % deployLocations.size();
            Pos buildLocation = deployLocations.at(randomIndex);

            // Build at that location.
            gameState.attemptSpawn(SCRAMBLER, buildLocation);
            
            // We don't have to remove the location since
            // units can occupy the same space.
        }
    }

    /// This returns a vector of positions not already occupied.
    /// @param locations A vector of locations to check.
    /// @return A new vector with no positions that are blocked.
    vector<Pos> AlgoStrategy::filterBlockedLocations(vector<Pos>& locations, GameState& gameState) {
        vector<Pos> filtered;
        for (Pos pos : locations) {
            // if (!gameState.gameMap.containsStationaryUnit(pos)) { TODO: uncomment after merge with game_map PR.
            if (true) {
                filtered.push_back(pos);
            }
        }
        return filtered;
    }

}
