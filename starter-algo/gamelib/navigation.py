import heapq
import math
import sys
import queue
from .util import debug_write

class Node:
    def __init__(self):
        self.visited_idealness = False
        self.visited_validate = False
        self.blocked = False
        self.pathlength = -1

'''
This class helps with pathfinding. We guarentee the results will
be accurate, but top players may want to write their own pathfinding
code to maximise time efficiancy
'''
class ShortestPathFinder:
    def __init__(self):
        self.HORIZONTAL = 1
        self.VERTICAL = 2

    def navigate_multiple_endpoints(self, start_point, end_points, game_state):
        #Initialize map 
        self.game_state = game_state
        self.game_map = [[Node() for x in range(self.game_state.ARENA_SIZE)] for y in range(self.game_state.ARENA_SIZE)]
        #Fill in walls
        for location in self.game_state.game_map:
            if self.game_state.contains_stationary_unit(location):
                self.game_map[location[0]][location[1]].blocked = True
        #Do pathfinding
        ideal_endpoints = self.idealness_search(start_point, end_points)
        self.validate(ideal_endpoints, end_points)
        return self.get_path(start_point, end_points)

    def idealness_search(self, start, end_points):
        '''
        Finds the most ideal tile in our 'pocket' of space to path to. The edge if it is available, 
        or the best self destruct location otherwise
        '''
        current = queue.Queue()
        current.put(start)
        best_idealness = self.get_idealness(start, end_points)
        most_ideal = start

        while not current.empty():
            search_location = current.get()
            for neighbor in self.get_neighbors(search_location):
                if not self.game_state.game_map.in_arena_bounds(neighbor) or self.game_map[neighbor[0]][neighbor[1]].blocked:
                    continue

                x, y = neighbor
                current_idealness = self.get_idealness(neighbor, end_points)

                if current_idealness > best_idealness:
                    best_idealness = current_idealness
                    most_ideal = neighbor

                if not self.game_map[x][y].visited_idealness and not self.game_map[x][y].blocked:
                    self.game_map[x][y].visited_idealness = True
                    current.put(neighbor)

        return most_ideal

    def get_neighbors(self, location):
        x, y = location
        return [[x, y + 1], [x, y - 1], [x + 1, y], [x - 1, y]]

    def get_direction_from_endpoints(self, end_points):
        point = end_points[0]
        x, y = point
        direction = [1, 1]
        if x < self.game_state.HALF_ARENA:
           direction[0] = -1
        if y < self.game_state.HALF_ARENA:
            direction[1] = -1
        return direction

    def get_idealness(self, location, end_points):
        if location in end_points:
            return sys.maxsize

        direction = self.get_direction_from_endpoints(end_points)

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

    def validate(self, ideal_tile, end_points):
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
            for neighbor in self.get_neighbors(current_location):
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

    def get_path(self, start_point, end_points):
        #GET THE PATH
        path = [start_point]
        current = start_point
        move_direction = 0

        while not self.game_map[current[0]][current[1]].pathlength == 0:
            #debug_write("current tile {} has cost {}".format(current, self.game_map[current[0]][current[1]].pathlength))
            next_move = self.choose_next_move(current, move_direction, end_points)
            #debug_write(next_move)

            if current[0] == next_move[0]:
                move_direction = self.VERTICAL
            else:
                move_direction = self.HORIZONTAL
            path.append(next_move)
            current = next_move
        
        debug_write(path)
        return path
  
    def choose_next_move(self, current_point, previous_move_direction, end_points):
        neighbors = self.get_neighbors(current_point)
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
            if not new_best and not self.better_direction(current_point, neighbor, ideal_neighbor, previous_move_direction, end_points):
                continue

            ideal_neighbor = neighbor
            best_pathlength = current_pathlength

        #debug_write("Gave unit at {} new tile {}".format(current_point, ideal_neighbor))
        return ideal_neighbor

    def better_direction(self, prev_tile, new_tile, prev_best, previous_move_direction, end_points):
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
        direction = self.get_direction_from_endpoints(end_points)
        if new_tile[1] == prev_best[1]: #If they both moved horizontal...
            if direction[0] == 1 and new_tile[0] > prev_best[0]: #If we moved right and right is our direction, we moved towards our direction
                return True 
            return False 
        if new_tile[0] == prev_best[0]: #If they both moved vertical...
            if direction[1] == 1 and new_tile[1] > prev_best[1]: #If we moved up and up is our direction, we moved towards our direction
                return True
            return False
        return True

    def print_map(self):
        for y in range(28):
            for x in range(28):
                node = self.game_map[x][28 - y - 1]
                if not node.blocked and not node.pathlength == -1:
                    self.print_justified(node.pathlength)
                else:
                    sys.stderr.write("   ")
            debug_write("")

    def print_justified(self, number):
        if number < 10 and number > -1:
            sys.stderr.write(" ")
        sys.stderr.write(str(number))
        sys.stderr.write(" ")
