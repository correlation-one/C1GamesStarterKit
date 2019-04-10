/*
Description: A header to contain a representation of the current game map.
Last Modified: 09 Apr 2019
Author: Isaac Draper, Ryan Draves
*/

#ifndef ALGO_MAP_H
#define ALGO_MAP_H

#include <vector>
#include <math.h>

#include "json11/json11.hpp"
#include "structs.h"
#include "enums.h"
#include "util.h"
#include "unit.h"
#include "customExceptions.h"

namespace terminal {

    using json11::Json;
    using std::vector;

    /// Holds data about the current game map and provides functions
    /// useful for getting information related to the map.
    class GameMap {
    public:
        GameMap(Json config);
        bool inArenaBounds(int x, int y) const;
        bool inArenaBounds(Pos pos) const;
        void getEdgeLocations(vector<Pos>& vec, const EDGE edge) const;
        void getEdges(vector<vector<Pos> >& vec);
        void addUnit(UNIT_TYPE unitType, int x, int y, int playerIndex, int hp = 0);
        void addUnit(UNIT_TYPE unitType, Pos pos, int playerIndex, int hp = 0);
        void removeUnits(Pos pos);
        void getLocationsInRange(vector<Pos>& locations, Pos pos, double radius);
        bool containsStationaryUnit(Pos pos) const;
        bool containsStationaryUnit(int x, int y) const;
        vector<GameUnit>& operator[](const Pos &pos);
        const vector<GameUnit>& operator[](const Pos &pos) const;
        vector<vector<GameUnit> >& operator[](int x);
        vector<vector<vector<GameUnit> > >::iterator begin();
        vector<vector<vector<GameUnit> > >::iterator end();
        void setVerbosity(VERBOSITY verbosityIn) { verbosity = verbosityIn; };
        string toString() const;
        string str() { return toString(); };
        string repr() { return toString(); };
        string printMap() { return toString(); };

        const int ARENA_SIZE = 28;
        const int HALF_ARENA = 14;

    private:
        void createEmptyGrid();
        double distanceBetweenLocations(Pos pos_1, Pos pos_2);

    public:
        Json config;
        vector<vector<vector<GameUnit> > > map;
        VERBOSITY verbosity;
    };

    /// This sends a representation of the GameMap object to a stream.
    /// @return The stream passed to the function.
    inline std::ostream& operator<<(std::ostream& os, GameMap const& gameMap) {
        os << gameMap.toString();
        return os;
    }

}

#endif
