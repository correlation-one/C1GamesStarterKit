/*
Description: A header to contain a representation of the current game map.
Last Modified: 09 Apr 2019
Author: Isaac Draper
*/

#ifndef ALGO_MAP_H
#define ALGO_MAP_H

#include <iostream>
#include <vector>

#include "json11/json11.hpp"
#include "structs.h"
#include "enums.h"
#include "util.h"
#include "unit.h"

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
        void getEdgeLocations(vector<Pos>& vec, EDGE edge) const;
        void addUnit(GameUnit unit);

        const int ARENA_SIZE = 28;
        const int HALF_ARENA = 14;

    private:
        void createEmptyGrid();

        Json config;
        vector<vector<vector<GameUnit>>> map;

    };

}

#endif
