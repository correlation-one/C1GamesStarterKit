/*
Description: A header for the path finder.
Last Modified: 08 Apr 2019
Author: Patrik Dobias
*/

#ifndef NAVIGATION_H
#define NAVIGATION_H

#include <limits>
#include <algorithm>
#include <vector>
#include <queue>

#include "GameLib/src/util.h"
#include "GameLib/src/structs.h"
#include "GameLib/src/gameState.h"

namespace terminal {

    using std::vector;

    /// Structure representating each location in gameMap.
    struct Node {
        bool visitedIdealness = false;
        bool visitedValidate = false;
        bool blocked = false;
        int pathLength = -1;
    };
    
    /// This class handles pathfinding.
    class ShortestPathFinder {
    public:
        ShortestPathFinder(const GameState& gameState);
        void initializeMap();
        void navigate_multiple_endpoints(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path);
        void printMap();
    private:
        Pos idealnessSearch(Pos startPoint, const vector<Pos>& endPoints);
        void getNeighbors(Pos location, vector<Pos>& neighbors);
        Pos getDirectionFromEndPoints(const vector<Pos>& endPoints);
        int getIdealness(Pos location, const vector<Pos>& endPoints);
        void validate(Pos idealTile, const vector<Pos>& endPoints);
        void getPath(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path);
        Pos chooseNextMove(Pos currentPoint, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints);
        bool betterDirection(Pos prevTile, Pos newTile, Pos prevBest, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints);
        void printJustified(int number);

        const GameState gameState;
        bool initialized;
        vector<vector<Node>> gameMap;
    };

}

#endif