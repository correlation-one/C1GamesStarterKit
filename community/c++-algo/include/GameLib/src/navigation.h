/*
Description: Runs pathfinding using terminal logic.
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

    /// Represents the last direction moved by a unit.
    enum MOVE_DIRECTION {
        NONE,                           ///< Means the unit has not moved yet.
        HORIZONTAL,                     ///< The unit moved horizontally last.
        VERTICAL                        ///< The unit moved vertically last.
    };

    /// Representats a location in the games map for pathfinding.
    struct Node {
        bool visitedIdealness;          ///< How good this node is to move towards the target point.
        bool visitedValidate;           ///< Whether this node has been validated.
        bool blocked;                   ///< Whether this node is blocked.
        int pathLength;                 ///< The number of steps to get to this node.

        /// Constructor for creating a Node.
        Node(): visitedIdealness(false), visitedValidate(false), blocked(false), pathLength(-1) {  }
    };
    
    /// This class finds the shortest path from a given
    /// start and end point. If one does not exists it
    /// returns the best path using terminal's pathing logic.
    class ShortestPathFinder {
    public:
        // Functions
        ShortestPathFinder(GameMap& gameMap);
        void navigateMultipleEndpoints(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path);
        void printMap();

    private:
        // Functions
        void initializeMap();
        Pos idealnessSearch(Pos startPoint, const vector<Pos>& endPoints);

        void getNeighbors(Pos location, vector<Pos>& neighbors);
        Pos getDirectionFromEndPoints(const vector<Pos>& endPoints);
        int getIdealness(Pos location, const vector<Pos>& endPoints);

        void validate(Pos idealTile, const vector<Pos>& endPoints);
        void getPath(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path);

        Pos chooseNextMove(Pos currentPoint, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints);
        bool betterDirection(Pos prevTile, Pos newTile, Pos prevBest, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints);
        void printJustified(int number);

        // Members
        GameMap gameMap;                ///< The map for the current state of the game.
        bool initialized;               ///< Whether or not the node map has been created.
        vector<vector<Node>> nodeMap;   ///< Represents a terminal map for pathfinding only.
    };

}

#endif