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

#include "util.h"
#include "structs.h"
#include "gameMap.h"

namespace terminal {

    using std::vector;

    /// Structure representating each location in gameMap.
    struct Node {
        bool visitedIdealness;
        bool visitedValidate;
        bool blocked;
        int pathLength;

        Node(): visitedIdealness(false), visitedValidate(false), blocked(false), pathLength(-1) {  }
    };
    
    /// This class handles pathfinding.
    class ShortestPathFinder {
    public:
        ShortestPathFinder(GameMap& gameMap);
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

        GameMap gameMap;
        bool initialized;
        vector<vector<Node>> nodeMap;
    };

}

#endif