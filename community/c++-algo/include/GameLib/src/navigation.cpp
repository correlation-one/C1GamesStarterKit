/*
Description: Implementations for the navigation header.
Last Modified: 08 Apr 2019
Author: Patrik Dobias
*/

#include "navigation.h"

namespace terminal {

    using std::numeric_limits;
    using std::find;
    using std::vector;
    using std::queue;
    using std::cerr;

    /// Constructor for ShortestPathFinder.
    /// @param gameMap A GameMap object representing the current game map (by reference).
    ShortestPathFinder::ShortestPathFinder(GameMap& gameMap) : gameMap(gameMap) { 
        initialized = false;
    }

    /// Initializes the navigation map with nodes.
    /// We cannot run pathfinding without this being called first.
    void ShortestPathFinder::initializeMap() {
        initialized = true;
        nodeMap.reserve(gameMap.ARENA_SIZE);

        for (unsigned int i = 0; i < gameMap.ARENA_SIZE; i++) {
            nodeMap.push_back(vector<Node>());
            nodeMap.at(i).reserve(gameMap.ARENA_SIZE);
            for (unsigned int j = 0; j < gameMap.ARENA_SIZE; j++) {
                nodeMap.at(i).push_back(Node());
            }
        }
    }

    /// Finds the path a unit would take to reach a set of endpoints.
    /// @param startPoint The starting location of the unit.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @param path An empty vector, which will be filled with path (by reference).
    void ShortestPathFinder::navigateMultipleEndpoints(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path) {
        if (gameMap.containsStationaryUnit(startPoint))
            return;

        initializeMap();

        for (unsigned int x = 0; x < gameMap.ARENA_SIZE; x++) 
            for (unsigned int y = 0; y < gameMap.ARENA_SIZE; y++) 
                if (gameMap.containsStationaryUnit(x, y)) 
                    nodeMap.at(x).at(y).blocked = true;

        Pos idealEndpoint = idealnessSearch(startPoint, endPoints);

        validate(idealEndpoint, endPoints);

        getPath(startPoint, endPoints, path);
    }

    /// Finds the most ideal endPoints.
    /// @param startPoint The starting location of the Unit.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @return Most ideal end point (location at target edge or self destruct location).
    Pos ShortestPathFinder::idealnessSearch(Pos startPoint, const vector<Pos>& endPoints) {
        queue<Pos> current;
        current.push(startPoint);
        int bestIdealness = getIdealness(startPoint, endPoints);
        nodeMap.at(startPoint.x).at(startPoint.y).visitedIdealness = true;
        Pos mostIdeal = startPoint;

        while(!current.empty()) {
            Pos searchLocation = current.front();
            current.pop();

            vector<Pos> neighbors;
            getNeighbors(searchLocation, neighbors);
            for(auto neighbor: neighbors) {
                int x = neighbor.x;
                int y = neighbor.y;

                if(!gameMap.inArenaBounds(neighbor) || nodeMap.at(x).at(y).blocked)
                    continue;
                
                int currentIdealness = getIdealness(neighbor, endPoints);

                if(currentIdealness > bestIdealness) {
                    bestIdealness = currentIdealness;
                    mostIdeal = neighbor;
                }

                if(!nodeMap.at(x).at(y).visitedIdealness) {
                    nodeMap.at(x).at(y).visitedIdealness = true;
                    current.push(neighbor);
                }
            }
        }

        return mostIdeal;
    }

    /// Gets locations adjacent to a location.
    /// @param location The location to get it's neighbors.
    /// @param neighbors An empty vector, which will be filled with neighbor locations (by reference).
    void ShortestPathFinder::getNeighbors(Pos location, vector<Pos>& neighbors) {
        neighbors.push_back({location.x    , location.y + 1});
        neighbors.push_back({location.x    , location.y - 1});
        neighbors.push_back({location.x + 1, location.y    });
        neighbors.push_back({location.x - 1, location.y    });
    }

    /// Gets direction for given endPoints.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @return A direction [x, y] representing the edge.
    Pos ShortestPathFinder::getDirectionFromEndPoints(const vector<Pos>& endPoints) {
        Pos direction = {1, 1};
        Pos point = endPoints[0];

        if(point.x < gameMap.HALF_ARENA)
            direction.x = -1;
        if(point.y < gameMap.HALF_ARENA)
            direction.y = -1;
        
        return direction;
    }

    /// Gets the idealness of a tile, the reachable tile the unit most wants to path to.
    /// Better self destruct locations are more ideal. The endpoints are perfectly ideal.
    /// @param location A location of the tile.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @return Idealness value of the location. 
    int ShortestPathFinder::getIdealness(Pos location, const vector<Pos>& endPoints) {
        if(find(endPoints.begin(), endPoints.end(), location) != endPoints.end())
            return numeric_limits<int>::max();

        Pos direction = getDirectionFromEndPoints(endPoints);
        int idealness = 0;
    
        if(direction.y == 1)
            idealness += 28 * location.y;
        else
            idealness += 28 * (27 - location.y);
        if(direction.x == 1)
            idealness += location.x;
        else
            idealness += (27 - location.x);

        return idealness;
    }

    /// Breadth first search of the grid, setting the pathlengths of each node.
    /// @param idealTile A best location, where path can end.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    void ShortestPathFinder::validate(Pos idealTile, const vector<Pos>& endPoints) {
        queue<Pos> current;

        if(find(endPoints.begin(), endPoints.end(), idealTile) != endPoints.end()) {
            for(auto location: endPoints) {
                current.push(location);
                nodeMap.at(location.x).at(location.y).pathLength = 0;
                nodeMap.at(location.x).at(location.y).visitedValidate = true;
            }
        } else {
            current.push(idealTile);
            nodeMap.at(idealTile.x).at(idealTile.y).pathLength = 0;
            nodeMap.at(idealTile.x).at(idealTile.y).visitedValidate = true;
        }

        while(!current.empty()) {
            Pos currentLocation = current.front();
            current.pop();
            Node currentNode = nodeMap.at(currentLocation.x).at(currentLocation.y);
            
            vector<Pos> neighbors;
            getNeighbors(currentLocation, neighbors);
            for(auto neighbor: neighbors) {
                int x = neighbor.x;
                int y = neighbor.y;

                if(!gameMap.inArenaBounds(neighbor) || nodeMap.at(x).at(y).blocked)
                    continue;

                if(!nodeMap.at(x).at(y).visitedValidate && !currentNode.blocked) {
                    nodeMap.at(x).at(y).pathLength = currentNode.pathLength + 1;
                    nodeMap.at(x).at(y).visitedValidate = true;
                    current.push(neighbor);
                }
            }
        }
    }

    /// Gets path from startPoint to one of the endPoints, based on values of each tile.
    /// @param startPoint The starting location of the unit.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @param path An empty vector, which will be filled with path (by reference).
    void ShortestPathFinder::getPath(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path) {
        path.push_back(startPoint);
        Pos current = startPoint;
        MOVE_DIRECTION moveDirection = NONE;

        while(nodeMap.at(current.x).at(current.y).pathLength != 0) {
            Pos nextMove = chooseNextMove(current, moveDirection, endPoints);

            if(current.x == nextMove.x)
                moveDirection = VERTICAL;
            else
                moveDirection = HORIZONTAL;

            path.push_back(nextMove);
            current = nextMove;
        }
    }

    /// Gets best 'next step' from the current location.
    /// @param currentPoint A current location.
    /// @param previousMoveDirection Represents wheter previous move was vertical or horizontal.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @return Next position from currentPoint.
    Pos ShortestPathFinder::chooseNextMove(Pos currentPoint, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints) {
        vector<Pos> neighbors;
        getNeighbors(currentPoint, neighbors);

        Pos idealNeighbor = currentPoint;
        int bestPathLength = nodeMap.at(currentPoint.x).at(currentPoint.y).pathLength;

        for(auto neighbor: neighbors) {
            int x = neighbor.x;
            int y = neighbor.y;

            if(!gameMap.inArenaBounds(neighbor) || nodeMap.at(x).at(y).blocked)
                continue;

            bool newBest = false;
            int currentPathLength = nodeMap.at(x).at(y).pathLength;

            if(currentPathLength > bestPathLength)
                continue;
            else if(currentPathLength < bestPathLength)
                newBest = true;

            if(!newBest && !betterDirection(currentPoint, neighbor, idealNeighbor, previousMoveDirection, endPoints))
                continue;
            
            idealNeighbor = neighbor;
            bestPathLength = currentPathLength;
        }

        return idealNeighbor;
    }

    /// Check whether newTile should be used in path or prevBest according to previou move.
    /// Should prioritize zig zag path.
    /// @param prevTile Current location of path.
    /// @param newTile Possible next location.
    /// @param prevBest Possible previous best next location.
    /// @param previousMoveDirection Represents wheter previous move was vertical or horizontal.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @return Whether the unit would rather move to the new one.
    bool ShortestPathFinder::betterDirection(Pos prevTile, Pos newTile, Pos prevBest, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints) {
        if(previousMoveDirection == HORIZONTAL && newTile.x != prevBest.x) {
            if(prevTile.y == newTile.y)
                return false;
            return true;
        }
        if(previousMoveDirection == VERTICAL && newTile.y != prevBest.y) {
            if(prevTile.x == newTile.x)
                return false;
            return true;
        }
        if(previousMoveDirection == NONE) {
            if(prevTile.y == newTile.y)
                return false;
            return true;
        }

        Pos direction = getDirectionFromEndPoints(endPoints);
        if(newTile.y == prevBest.y) {
            if(direction.x == 1 && newTile.x > prevBest.x)
                return true;
            if(direction.x == -1 && newTile.x < prevBest.x)
                return true;
            return false;
        }
        if(newTile.x == prevBest.x) {
            if(direction.y == 1 && newTile.y > prevBest.y)
                return true;
            if(direction.y == -1 && newTile.y < prevBest.y)
                return true;
            return false;
        }
        return true;
    }
    
    /// Prints an ASCII version of the current node map for debug purposes.
    /// It prints the length of each node from the start position.
    void ShortestPathFinder::printMap() {
        if(!initialized) {
            Util::debugWrite("Attempted to print_map before pathfinder initialization. Use 'this_object.initialize_map(game_state)' to initialize the map first");
            return;
        }

        for(unsigned int y = 0; y < gameMap.ARENA_SIZE; y++) {
            for(unsigned int x = 0; x < gameMap.ARENA_SIZE; x++) {
                Node node = nodeMap.at(x).at(28 - y - 1);
                if(!node.blocked && node.pathLength != -1)
                    printJustified(node.pathLength);
                else
                    cerr << "   ";
            }
            Util::debugWrite("");
        }
    }
    
    /// Prints a number between 100 and -10 in 3 spaces.
    void ShortestPathFinder::printJustified(int number) {
        if(number < 10 && number > -1)
            cerr << " ";
        cerr << number << " ";
    }
}