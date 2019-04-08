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
    ShortestPathFinder::ShortestPathFinder(const GameState& gameState) : gameState(gameState) { 
        initialized = false;
    }

    /// Initializes the map.
    /// @param gameState A GameState object representing the gamestate we want to find path for (by reference).
    void ShortestPathFinder::initializeMap() {
        initialized = true;
        gameMap.reserve(gameState.ARENA_SIZE);

        for (size_t i = 0; i < gameState.ARENA_SIZE; i++) {
            gameMap.push_back(vector<Node>());
            gameMap[i].reserve(gameState.ARENA_SIZE);
            for (size_t j = 0; j < gameState.ARENA_SIZE; j++) {
                gameMap[i].push_back(Node());
            }
        }
    }

    /// Finds the path a unit would take to reach a set of endpoints.
    /// @param startPoint The starting location of the unit.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @param gameState A GameState object representing the current game state (by reference).
    /// @param path An empty vector, which will be filled with path (by reference).
    void ShortestPathFinder::navigate_multiple_endpoints(Pos startPoint, const vector<Pos>& endPoints, vector<Pos>& path) {
        if (gameState.containsStationaryUnit(startPoint))
            return;

        initializeMap();

        for (auto location: gameState.gameMap)
            if (gameState.containsStationaryUnit(location))
                gameMap[location.x][location.y].blocked = true;

        Pos idealEndpoint = idealnessSearch(startPoint, endPoints);

        validate(idealEndpoint, endPoints);

        getPath(startPoint, endPoints, path);
    }

    /// Finds the most ideal endPoints.
    /// @param startPoint The starting location of the Unit.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @param gameState A GameState object representing the current game state.
    /// @return Most ideal end point.
    Pos ShortestPathFinder::idealnessSearch(Pos startPoint, const vector<Pos>& endPoints) {
        queue<Pos> current;
        current.push(startPoint);
        int bestIdealness = getIdealness(startPoint, endPoints);
        gameMap[startPoint.x][startPoint.y].visitedIdealness = true;
        Pos mostIdeal = startPoint;

        while(!current.empty()) {
            Pos searchLocation = current.front();
            current.pop();

            vector<Pos> neighbors;
            getNeighbors(searchLocation, neighbors);
            for(auto neighbor: neighbors) {
                int x = neighbor.x;
                int y = neighbor.y;

                if(!gameState.gameMap.inArenaBounds(neighbor) || gameMap[x][y].blocked)
                    continue;
                
                int currentIdealness = getIdealness(neighbor, endPoints);

                if(currentIdealness > bestIdealness) {
                    bestIdealness = currentIdealness;
                    mostIdeal = neighbor;
                }

                if(!gameMap[x][y].visitedIdealness) {
                    gameMap[x][y].visitedIdealness = true;
                    current.push(neighbor);
                }
            }
        }

        return mostIdeal;
    }

    /// Gets locations adjacent to a location
    /// @param location
    /// @param neighbors An empty vector, which will be filled with neighbor locations (by reference).
    void ShortestPathFinder::getNeighbors(Pos location, vector<Pos>& neighbors) {
        neighbors.push_back({location.x    , location.y + 1});
        neighbors.push_back({location.x    , location.y - 1});
        neighbors.push_back({location.x + 1, location.y    });
        neighbors.push_back({location.x - 1, location.y    });
    }

    /// Gets direction for given endPoints
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @param gameState A GameState object representing the current game state (by reference).
    /// @return A direction [x,y] representing the edge.
    Pos ShortestPathFinder::getDirectionFromEndPoints(const vector<Pos>& endPoints) {
        Pos direction = {1, 1};
        Pos point = endPoints[0];

        if(point.x < gameState.HALF_ARENA)
            direction.x = -1;
        if(point.y < gameState.HALF_ARENA)
            direction.y = -1;
        
        return direction;
    }

    /// Gets the idealness of a tile, the reachable tile the unit most wants to path to.
    /// Better self destruct locations are more ideal. The endpoints are perfectly ideal.
    /// @param location A location of the tile.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @param gameState A GameState object representing the current game state (by reference).
    /// @return Value of the location. 
    int ShortestPathFinder::getIdealness(Pos location, const vector<Pos>& endPoints) {
        if(find(endPoints.begin(), endPoints.end(), location) == endPoints.end())
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
                gameMap[location.x][location.y].pathLength = 0;
                gameMap[location.x][location.y].visitedValidate = true;
            }
        } else {
            current.push(idealTile);
            gameMap[idealTile.x][idealTile.y].pathLength = 0;
            gameMap[idealTile.x][idealTile.y].visitedValidate = true;
        }

        while(!current.empty()) {
            Pos currentLocation = current.front();
            current.pop();
            Node currentNode = gameMap[currentLocation.x][currentLocation.y];
            
            vector<Pos> neighbors;
            getNeighbors(currentLocation, neighbors);
            for(auto neighbor: neighbors) {
                int x = neighbor.x;
                int y = neighbor.y;

                if(!gameState.gameMap.inArenaBounds(neighbor) || gameMap[x][y].blocked)
                    continue;

                Node neighborNode = gameMap[x][y];
                if(!neighborNode.visitedValidate && !currentNode.blocked) {
                    neighborNode.pathLength = currentNode.pathLength + 1;
                    neighborNode.visitedValidate = true;
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

        while(gameMap[current.x][current.y].pathLength != 0) {
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
        int bestPathLength = gameMap[currentPoint.x][currentPoint.y].pathLength;

        for(auto neighbor: neighbors) {
            int x = neighbor.x;
            int y = neighbor.y;

            if(!gameState.gameMap.inArenaBounds(neighbor) || gameMap[x][y].blocked)
                continue;

            bool newBest = false;
            int currentPathLength = gameMap[x][y].pathLength;

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
    /// Should prioritize zig zag path 
    /// @param prevTile Current location of path.
    /// @param newTile Possible next location.
    /// @param prevBest Possible previous best next location.
    /// @param previousMoveDirection Represents wheter previous move was vertical or horizontal.
    /// @param endPoints A vector of end locations for the unit, should be a list of edge locations (by reference).
    /// @return Whether the unit would rather move to the new one
    bool ShortestPathFinder::betterDirection(Pos prevTile, Pos newTile, Pos prevBest, MOVE_DIRECTION previousMoveDirection, const vector<Pos>& endPoints) {
        if(previousMoveDirection == HORIZONTAL && newTile.x == prevBest.x) {
            if(prevTile.y == newTile.y)
                return false;
            return true;
        }
        if(previousMoveDirection == VERTICAL && newTile.y == prevBest.y) {
            if(prevTile.x == newTile.x)
                return false;
            return true;
        }
        if(previousMoveDirection == 0) {
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
    
    /// Prints an ASCII version of the current game map for debug purposes
    void ShortestPathFinder::printMap() {
        if(!initialized) {
            Util::debugWrite("Attempted to print_map before pathfinder initialization. Use 'this_object.initialize_map(game_state)' to initialize the map first");
            return;
        }

        for(size_t y = 0; y < 28; y++) {
            for(size_t x = 0; x < 28; x++) {
                Node node = gameMap[x][28 - y - 1];
                if(!node.blocked and !node.pathLength == -1)
                    printJustified(node.pathLength);
                else
                    cerr << "   ";
            }
            Util::debugWrite("");
        }
    }
    
    /// Prints a number between 100 and -10 in 3 spaces
    void ShortestPathFinder::printJustified(int number) {
        if(number < 10 && number > -1)
            cerr << " ";
        cerr << number << " ";
    }
}