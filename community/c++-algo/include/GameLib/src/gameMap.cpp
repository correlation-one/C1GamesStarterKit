/*
Description: Implementations for the algoMap header.
Last Modified: 10 Apr 2019
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
        this->verbosity = WARNING;
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
    void GameMap::getEdgeLocations(vector<Pos>& vec, const EDGE edge) const {
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
                Util::printError<GameMapException>("Invalid edge requested", INVARIANT, verbosity);
        }
        }
    }

    /// Fills out a vector of all the edges
    /// @param vec A vector of { topRight, topLeft, bottomLeft, bottomRight } edges
    void GameMap::getEdges(vector<vector<Pos> >& vec) {
        vector<Pos> topRight, topLeft, bottomLeft, bottomRight;
        getEdgeLocations(topRight, TOP_RIGHT);
        getEdgeLocations(topLeft, TOP_LEFT);
        getEdgeLocations(bottomLeft, BOTTOM_LEFT);
        getEdgeLocations(bottomRight, BOTTOM_RIGHT);
        vec.emplace_back(topRight);
        vec.emplace_back(topLeft);
        vec.emplace_back(bottomLeft);
        vec.emplace_back(bottomRight);
    }

    /// Add a single GameUnit to the map at the given location.
    /// This does not send it to the engine, it simply lets you create any
    /// map position you want to experiment with.
    /// @param unitType The type of unit to add. Stationary units will replace 
    /// @param pos The position to add the unit at.
    /// @param playerIndex The player to add the unit for.
    /// @param hp The health of the unit (default is max health).
    void GameMap::addUnit(UNIT_TYPE unitType, Pos pos, int playerIndex, double hp) {
        if (!inArenaBounds(pos)) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        if (playerIndex < 0 || playerIndex > 1) throw PlayerIndexException();
        // Stability of 0 will default the unit to max_stability
        GameUnit newUnit = GameUnit(unitType, config, hp, playerIndex, pos[0], pos[1]);
        if (!newUnit.stationary) {
            map.at(pos.x).at(pos.y).push_back(newUnit);
        }
        else {
            size_t size = map.at(pos.x).at(pos.y).size();
            if (size > 0 && newUnit.unitType != REMOVE)
                Util::printError<GameMapException>("Error placing a stationary unit in an occupied location", INVARIANT, verbosity);
            else if ((size != 1 || (size > 0 && !map.at(pos.x).at(pos.y).at(0).stationary))
                && newUnit.unitType == REMOVE)
                Util::printError<GameMapException>("Error placing remove; 1 stationary unit not found", INVARIANT, verbosity);
            // Clearing the vector for firewalls is not necessary, as we verified above
            map.at(pos.x).at(pos.y).push_back(newUnit);
        }
    }


    /// Add a single GameUnit to the map at the given location.
    /// This does not send it to the engine, it simply lets you create any
    /// map position you want to experiment with.
    /// @param unitType The type of unit to add. Stationary units will replace 
    /// @param x The x position to add the unit at.
    /// @param y The y position to add the unit at.
    /// @param playerIndex The player to add the unit for.
    /// @param hp The health of the unit (default is max health).
    void GameMap::addUnit(UNIT_TYPE unitType, int x, int y, int playerIndex, double hp) {
        addUnit(unitType, Pos(x, y), playerIndex, hp);
    }

    /// Remove all GameUnits from the game map at the location. Throw an error if it's empty.
    /// @param pos Position to clear from the game map
    void GameMap::removeUnits(Pos pos) {
        if (!inArenaBounds(pos)) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        if (map.at(pos.x).at(pos.y).size() == 0) Util::printError<GameMapException>("Error trying to remove 0 units", WARNING, verbosity);
        map.at(pos.x).at(pos.y).clear();
    }

    /// Takes a position and radius and fills a vector with locations in its range
    /// @param locations A vector passed by reference to return the values.
    /// @param pos The position to find locatins in range from.
    /// @param radius The radius of the circle to get locations from.
    void GameMap::getLocationsInRange(vector<Pos>& locations, Pos pos, double radius) {
        if (radius < 0 || radius > ARENA_SIZE)
            Util::printError<GameMapException>("Error getting locations in range with that radius", INVARIANT, verbosity);
        if (!inArenaBounds(pos)) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        for (int i = (int)(pos.x - radius); i < (int)(pos.x + radius + 1); i++) {
            for (int j = (int)(pos.y - radius); j < (int)(pos.y + radius + 1); j++) {
                Pos new_pos = { i, j };
                if (inArenaBounds(new_pos) && distanceBetweenLocations(pos, new_pos) < radius + 0.51) {
                    locations.push_back(new_pos);
                }
            }
        }
    }

    /// Boolean return of a stationary unit located at the position.
    /// @param pos Position to check on the map.
    /// @return Boolean answer to a stationary unit at the location.
    bool GameMap::containsStationaryUnit(Pos pos) const {
        if (!inArenaBounds(pos)) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        if (map.at(pos.x).at(pos.y).size() > 0) {
            switch (map.at(pos.x).at(pos.y).at(0).unitType) {
                case FILTER:
                case ENCRYPTOR:
                case DESTRUCTOR:
                    return true;
                    break;
                default:
                    return false;
            }
        }
        return false;
    }

    /// Boolean return of a stationary unit located at the position.
    /// @param x X coordinate to check on the map.
    /// @param y Y coordinate to check on the map.
    /// @return Boolean answer to a stationary unit at the location.
    bool GameMap::containsStationaryUnit(int x, int y) const {
        return containsStationaryUnit(Pos(x, y));
    }

    /// Helper function to get the euclidean distance between two locations
    /// @param pos_1 First position.
    /// @param pos_2 Second position.
    /// @return Euclidean distance between two positions.
    double GameMap::distanceBetweenLocations(Pos pos_1, Pos pos_2) {
        return sqrt(pow(pos_1.x - pos_2.x, 2) + pow(pos_1.y - pos_2.y, 2));
    }

    /// Overloaded [Pos] operator enables access in the game map with a Pos.
    /// @param pos Position to index into the map.
    /// @return A reference to the vector of GameUnits at the location.
    vector<GameUnit>& GameMap::operator[](const Pos &pos) {
        if (!inArenaBounds(pos)) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        return map.at(pos.x).at(pos.y);
    }

    /// Overloaded const [Pos] operator enables const access in the game map with a Pos.
    /// @param pos Position to index into the map.
    /// @return A reference to the vector of GameUnits at the location.
    const vector<GameUnit>& GameMap::operator[](const Pos &pos) const {
        if (!inArenaBounds(pos)) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        return map.at(pos.x).at(pos.y);
    }

    /// Overloaded [int] operator enables access in the game map with [x][y]
    /// @param x X coordinate to index into the map.
    /// @return A reference to the column of the game map at coordinate X.
    vector<vector<GameUnit> >& GameMap::operator[](int x) {
        // y = 13 and 14 are true to any valid x value
        if (!inArenaBounds(Pos(x, 13))) Util::printError<PosException>("Out of bounds exception", CRASH, verbosity);
        return map.at(x);
    }

    /// Iterator function to help auto range through the game map
    /// @return A vector begin iterator through the columns of the game map
    vector<vector<vector<GameUnit> > >::iterator GameMap::begin() {
        return map.begin();
    }

    /// Iterator function to help auto range through the game map
    /// @return A vector end iterator through the columns of the game map
    vector<vector<vector<GameUnit> > >::iterator GameMap::end() {
        return map.end();
    }

    /// Prints an ACSII version of the current game map for debug purposes
    /// @return A very large string that represents the GameMap.
    string GameMap::toString() const {
        string ret = "";
        for (int y = 0; y < ARENA_SIZE; y++) {
            for (int x = 0; x < ARENA_SIZE; x++) {
                Pos location = { x, ARENA_SIZE - y - 1 };
                const vector<GameUnit> &stack = map.at(location.x).at(location.y);
                if (!inArenaBounds(location))
                    ret += " - ";
                else if (stack.size() == 0)
                    ret += " + ";
                else {
                    ret += stack.at(0).toString() + " ";
                }
            }
            ret += "\n";
        }
        return ret;
    }

}
