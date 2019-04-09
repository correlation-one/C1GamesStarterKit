/*
Description: Implementations for the algoMap header.
Last Modified: 09 Apr 2019
Author: Isaac Draper
*/

#include "gameMap.h"

namespace terminal {

    using std::vector;

    /// Constructor for GameMap which requires a configuration Json object.
    /// @param configuration A Json object containing information about the game.
    GameMap::GameMap(Json config) {
        this->config = config;
        createEmptyGrid();
    }

    /// Fills map with an emtpy grid of dimensions AREA_SIZE.
    void GameMap::createEmptyGrid() {
        map.resize(ARENA_SIZE);
        for (int x = 0; x < ARENA_SIZE; ++x)
            map.at(x).resize(ARENA_SIZE);
    }

    /// Checks if a position is inside the diamond shaped game board.
    /// @param x The x position.
    /// @param y The y position.
    bool GameMap::inArenaBounds(int x, int y) const {
        int rowSize = y + 1;
        int startX = HALF_ARENA - rowSize;
        int endX = startX + (2 * rowSize) - 1;
        const bool topHalfCheck = y < HALF_ARENA && x >= startX && x <= endX;

        rowSize = (ARENA_SIZE - 1 - y) + 1;
        startX = HALF_ARENA - rowSize;
        endX = startX + (2 * rowSize) - 1;
        const bool bottomHalfCheck = y >= HALF_ARENA && x >= startX && x <= endX;

        return bottomHalfCheck || topHalfCheck;
    }

    /// Checks if a position is inside the diamond shaped game board.
    /// @param pos The position to check.
    bool GameMap::inArenaBounds(Pos pos) const {
        return inArenaBounds(pos.x, pos.y);
    }

    /// Takes an edge and fills a vector with a list of locations.
    /// @param vec A vector passed by reference you would like to fill.
    /// @param edge The edge to get units for.
    void GameMap::getEdgeLocations(vector<Pos>& vec, EDGE edge) const {
        int x, y;
        switch (edge) {
        case TOP_RIGHT: {
            for (int i = 0; i < HALF_ARENA; ++i) {
                x = HALF_ARENA + i;
                y = ARENA_SIZE - 1 - i;
                vec.push_back(Pos{ x, y });
            }
            break;
        }
        case TOP_LEFT: {
            for (int i = 0; i < HALF_ARENA; ++i) {
                x = HALF_ARENA - 1 - i;
                y = ARENA_SIZE - 1 - i;
                vec.push_back(Pos{ x, y });
            }
            break;
        }
        case BOTTOM_LEFT: {
            for (int i = 0; i < HALF_ARENA; ++i) {
                x = HALF_ARENA - 1 - i;
                y = i;
                vec.push_back(Pos{ x, y });
            }
            break;
        }
        case BOTTOM_RIGHT: {
            for (int i = 0; i < HALF_ARENA; ++i) {
                x = HALF_ARENA + i;
                y = i;
                vec.push_back(Pos{ x, y });
            }
            break;
        }
        default: {
            // TODO: throw gameMap error
        }
        }
    }

    /// Add an existing GameUnit to the map at the given location.
    /// This does not send it to the engine, it simply lets you create any
    /// map position you want.
    /// @param unitType The type of unit to add.
    void GameMap::addUnit(GameUnit unit) {
        // TODO: add the unit (waiting for merge)
    }

}
