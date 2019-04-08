/*
Description: Implementations for the algoMap header.
Last Modified: 08 Apr 2019
Author: Isaac Draper, Ryan Draves
*/

#include "gameMap.h"

namespace terminal {

    using json11::Json;
    using std::vector;

    /// Constructor for GameMap which requires a configuration Json object.
    /// @param configuration A Json object containing information about the game.
    GameMap::GameMap(Json config) {
        this->config = config;
        createEmptyGrid();
    }

    /// Fills map with an emtpy grid of dimensions AREA_SIZE.
    void GameMap::createEmptyGrid() {
        map.reserve(ARENA_SIZE);

        for (int x = 0; x < ARENA_SIZE; ++x) {
            map.at(x).reserve(ARENA_SIZE);
            map.push_back(vector<vector<GameUnit>>());

            for (int y = 0; y < ARENA_SIZE; ++y) {
                map.at(x).at(y) = vector<GameUnit>();
            }
        }
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
    void GameMap::getEdgeLocations(vector<Pos>& vec, EDGE edge) {
        int x, y;
        switch (edge) {
            case TOP_RIGHT: {
                for (int i = 0; i < HALF_ARENA; ++i) {
                    x = HALF_ARENA + i;
                    y = ARENA_SIZE - 1 - i;
                    vec.push_back(Pos{ x, y});
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

    /// Add a single GameUnit to the map at the given location.
    /// @param unitType The type of unit to add. Stationary units will replace 
    /// @param pos The position to add the unit at.
    /// @param playerIndex The player to add the unit for.
    void GameMap::addUnit(UNIT_TYPE unitType, Pos pos, int playerIndex) {
        if (!inArenaBounds(pos)) throw PosException();
        if (playerIndex < 0 || playerIndex > 1) throw PlayerIndexException();
        // Stability of 0 will default the unit to max_stability
        GameUnit newUnit = GameUnit(unitType, config, 0, playerIndex, pos[0], pos[1]);
        if (!newUnit.stationary) {
            map.at(pos.x).at(pos.y).push_back(newUnit);
        }
        else {
            uint size = map.at(pos.x).at(pos.y).size();
            if (size > 0 && newUnit.unitType != REMOVE)
                throw GameMapException("Error placing a stationary unit in an occupied location");
            else if ((size != 1 || (size > 0 && !map.at(pos.x).at(pos.y).at(0).stationary))
                && newUnit.unitType == REMOVE)
                throw GameMapException("Error placing remove; 1 stationary unit not found");
            // Clearing the vector for firewalls is not necessary, as we verified above
            map.at(pos.x).at(pos.y).push_back(newUnit);
        }
    }

    /// Overloaded [Pos] operator enables access in the game map with a Pos.
    /// @param pos Position to index into the map.
    /// @return A reference to the vector of GameUnits at the location.
    vector<GameUnit>& GameMap::operator[](Pos pos) {
        return map.at(pos.x).at(pos.y);
    }

    /// Overloaded [int] operator enables access in the game map with [x][y]
    /// @param x X coordinate to index into the map.
    /// @return A reference to the column of the game map at coordinate X.
    vector<vector<GameUnit> >& GameMap::operator[](int x) {
        return map.at(x);
    }
}
