import heapq
import math
import sys
import queue
from .util import debug_write

class Node:
    """A pathfinding node

    Attributes :
        * visited_idealness (bool): Have we visited this node during the idealness search step?
        * visited_validate (bool): Have we visited this node during the validation step?
        * blocked (bool): Is there a structures at this node's location
        * pathlength: The distance between this node and the target location

    """
    def __init__(self):
        self.visited_idealness = False
        self.visited_validate = False
        self.blocked = False
        self.pathlength = -1

"""
This class helps with pathfinding. We guarantee the results will
be accurate, but top players may want to write their own pathfinding
code to maximise time efficiency
"""
class ShortestPathFinder:
    """Handles pathfinding

    Attributes :
        * HORIZONTAL (int): A constant representing a horizontal movement
        * VERTICAL (int): A constant representing a vertical movement

        * game_state (:obj: GameState): The current gamestate
        * game_map (:obj: GameMap): The current gamemap

    """
    def __init__(self):
        self.HORIZONTAL = 1
        self.VERTICAL = 2
        self.initialized = False

    def initialize_map(self, game_state):
        """Initializes the map

        Args:
            game_state: A GameState object representing the gamestate we want to traverse
        """
        #Initialize map 
        self.initialized = True
        self.game_state = game_state
        self.game_map = [[Node() for x in range(self.game_state.ARENA_SIZE)] for y in range(self.game_state.ARENA_SIZE)]

    def navigate_multiple_endpoints(self, start_point, end_points, game_state):
        """Finds the path a unit would take to reach a set of endpoints

        Args:
            * start_point: The starting location of the unit
            * end_points: The end points of the unit, should be a list of edge locations
            * game_state: The current game state

        Returns:
            The path a unit at start_point would take when trying to reach end_points given the current game state.
            Note that this path can change if a tower is destroyed during pathing, or if you or your enemy places structures.

        """
        if game_state.contains_stationary_unit(start_point):
            return

        #Initialize map 
        self.initialize_map(game_state)
        #Fill in walls
        for location in self.game_state.game_map:
            if self.game_state.contains_stationary_unit(location):
                self.game_map[location[0]][location[1]].blocked = True
        #Do pathfinding
        ideal_endpoints = self._idealness_search(start_point, end_points)
        self._validate(ideal_endpoints, end_points)
        return self._get_path(start_point, end_points)

    def _idealness_search(self, start, end_points):
        """
        Finds the most ideal tile in our 'pocket' of pathable space. 
        The edge if it is available, or the best self destruct location otherwise
        """
        current = queue.Queue()
        current.put(start)
        best_idealness = self._get_idealness(start, end_points)
        self.game_map[start[0]][start[1]].visited_idealness = True
        most_ideal = start

        while not current.empty():
            search_location = current.get()
            for neighbor in self._get_neighbors(search_location):
                if not self.game_state.game_map.in_arena_bounds(neighbor) or self.game_map[neighbor[0]][neighbor[1]].blocked:
                    continue

                x, y = neighbor
                current_idealness = self._get_idealness(neighbor, end_points)

                if current_idealness > best_idealness:
                    best_idealness = current_idealness
                    most_ideal = neighbor

                if not self.game_map[x][y].visited_idealness and not self.game_map[x][y].blocked:
                    self.game_map[x][y].visited_idealness = True
                    current.put(neighbor)

        return most_ideal

    def _get_neighbors(self, location):
        """Get the locations adjacent to a location
        """
        x, y = location
        return [[x, y + 1], [x, y - 1], [x + 1, y], [x - 1, y]]

    def _get_direction_from_endpoints(self, end_points):
        """Prints a message to the games debug output

        Args:
            * end_points: A set of endpoints, should be an edge 

        Returns:
            A direction [x,y] representing the edge. For example, [1,1] for the top right and [-1, 1] for the top left

        """
        point = end_points[0]
        x, y = point
        direction = [1, 1]
        if x < self.game_state.HALF_ARENA:
           direction[0] = -1
        if y < self.game_state.HALF_ARENA:
            direction[1] = -1
        return direction

    def _get_idealness(self, location, end_points):
        """Get the idealness of a tile, the reachable tile the unit most wants to path to.
        Better self destruct locations are more ideal. The endpoints are perfectly ideal. 

        Returns:
            A location the unit will attempt to reach
        """
        if location in end_points:
            return sys.maxsize

        direction = self._get_direction_from_endpoints(end_points)

        idealness = 0
        if direction[1] == 1:
            idealness += 28 * location[1]
        else: 
            idealness += 28 * (27 - location[1])
        if direction[0] == 1:
            idealness += location[0]
        else: 
            idealness += (27 - location[0])

        return idealness

    def _validate(self, ideal_tile, end_points):
        """Breadth first search of the grid, setting the pathlengths of each node

        """
        #VALDIATION
        #Add our most ideal tiles to current
        current = queue.Queue()
        if ideal_tile in end_points:
            for location in end_points:
               current.put(location)
               #Set current pathlength to 0
               self.game_map[location[0]][location[1]].pathlength = 0
               self.game_map[location[0]][location[1]].visited_validate = True
        else:
            current.put(ideal_tile)
            self.game_map[ideal_tile[0]][ideal_tile[1]].pathlength = 0
            self.game_map[ideal_tile[0]][ideal_tile[1]].visited_validate = True

        #While current is not empty
        while not current.empty():
            current_location = current.get()
            current_node = self.game_map[current_location[0]][current_location[1]]
            for neighbor in self._get_neighbors(current_location):
                if not self.game_state.game_map.in_arena_bounds(neighbor) or self.game_map[neighbor[0]][neighbor[1]].blocked:
                    continue

                neighbor_node = self.game_map[neighbor[0]][neighbor[1]]
                if not neighbor_node.visited_validate and not current_node.blocked:
                    neighbor_node.pathlength = current_node.pathlength + 1
                    neighbor_node.visited_validate = True
                    current.put(neighbor)

        #debug_write("Print after validate")
        #self.print_map()
        return

    def _get_path(self, start_point, end_points):
        """Once all nodes are validated, and a target is found, the unit can path to its target

        """
        #GET THE PATH
        path = [start_point]
        current = start_point
        move_direction = 0

        while not self.game_map[current[0]][current[1]].pathlength == 0:
            #debug_write("current tile {} has cost {}".format(current, self.game_map[current[0]][current[1]].pathlength))
            next_move = self._choose_next_move(current, move_direction, end_points)
            #debug_write(next_move)

            if current[0] == next_move[0]:
                move_direction = self.VERTICAL
            else:
                move_direction = self.HORIZONTAL
            path.append(next_move)
            current = next_move
        
        #debug_write(path)
        return path
  
    def _choose_next_move(self, current_point, previous_move_direction, end_points):
        """Given the current location and adjacent locations, return the best 'next step' for a given unit to take
        """
        neighbors = self._get_neighbors(current_point)
        #debug_write("Unit at {} previously moved {} and has these neighbors {}".format(current_point, previous_move_direction, neighbors))

        ideal_neighbor = current_point
        best_pathlength = self.game_map[current_point[0]][current_point[1]].pathlength
        for neighbor in neighbors:
            #debug_write("Comparing champ {} and contender {}".format(ideal_neighbor, neighbor))
            if not self.game_state.game_map.in_arena_bounds(neighbor) or self.game_map[neighbor[0]][neighbor[1]].blocked:
                continue

            new_best = False
            x, y = neighbor
            current_pathlength = self.game_map[x][y].pathlength

            #Filter by pathlength
            if current_pathlength > best_pathlength:
                continue
            elif current_pathlength < best_pathlength:
                #debug_write("Contender has better pathlength at {} vs champs {}".format(current_pathlength, best_pathlength))
                new_best = True

            #Filter by direction based on prev move
            if not new_best and not self._better_direction(current_point, neighbor, ideal_neighbor, previous_move_direction, end_points):
                continue

            ideal_neighbor = neighbor
            best_pathlength = current_pathlength

        #debug_write("Gave unit at {} new tile {}".format(current_point, ideal_neighbor))
        return ideal_neighbor

    def _better_direction(self, prev_tile, new_tile, prev_best, previous_move_direction, end_points):
        """Compare two tiles and return True if the unit would rather move to the new one

        """
        #True if we are moving in a different direction than prev move and prev is not
        #If we previously moved horizontal, and now one of our options has a different x position then the other (the two options are not up/down)
        if previous_move_direction == self.HORIZONTAL and not new_tile[0] == prev_best[0]:
            #We want to go up now. If we have not changed our y, we are not going up
            if prev_tile[1] == new_tile[1]:
                return False 
            return True
        if previous_move_direction == self.VERTICAL and not new_tile[1] == prev_best[1]:
            if prev_tile[0] == new_tile[0]:
                #debug_write("contender {} has the same x coord as prev tile {} so we will keep best move {}".format(new_tile, prev_tile, prev_best))
                return False
            return True
        if previous_move_direction == 0: 
            if prev_tile[1] == new_tile[1]: 
                return False
            return True
        
        #To make it here, both moves are on the same axis 
        direction = self._get_direction_from_endpoints(end_points)
        if new_tile[1] == prev_best[1]: #If they both moved horizontal...
            if direction[0] == 1 and new_tile[0] > prev_best[0]: #If we moved right and right is our direction, we moved towards our direction
                return True 
            if direction[0] == -1 and new_tile[0] < prev_best[0]: #If we moved left and left is our direction, we moved towards our direction
                return True 
            return False 
        if new_tile[0] == prev_best[0]: #If they both moved vertical...
            if direction[1] == 1 and new_tile[1] > prev_best[1]: #If we moved up and up is our direction, we moved towards our direction
                return True
            if direction[1] == -1 and new_tile[1] < prev_best[1]: #If we moved down and down is our direction, we moved towards our direction
                return True
            return False
        return True

    def print_map(self):
        """Prints an ASCII version of the current game map for debug purposes

        """
        if not self.initialized:
            debug_write("Attempted to print_map before pathfinder initialization. Use 'this_object.initialize_map(game_state)' to initialize the map first")
            return

        for y in range(28):
            for x in range(28):
                node = self.game_map[x][28 - y - 1]
                if not node.blocked and not node.pathlength == -1:
                    self._print_justified(node.pathlength)
                else:
                    sys.stderr.write("   ")
            debug_write("")

    def _print_justified(self, number):
        """Prints a number between 100 and -10 in 3 spaces

        """
        if number < 10 and number > -1:
            sys.stderr.write(" ")
        sys.stderr.write(str(number))
        sys.stderr.write(" ")
