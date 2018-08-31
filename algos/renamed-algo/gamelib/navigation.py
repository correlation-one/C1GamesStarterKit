import heapq
import math
import sys


# Needed for the heapq to work since you can't make a compartor function that takes in Nodes for it and uses endpoints
current_end_points = []


def get_travel_cost_between_nodes(n1, n2):
    '''
    Returns the travel cost between nodes 1 space from another. Note, adds a small penalty so that it creates a zigzag
    pattern that exists in the actual game so that units behave more predictably when theres more than one shortest path
    '''
    if n1.x == n2.x or n1.y == n2.y:
        extra_cost = 0
        if n1.parent is None:
            if n1.x != n2.x:  # horizontal movement is penalized on first move
                extra_cost += .0001
        else:
            parent_horizontal = (n1.y == n1.parent.y)
            current_horizontal = (n1.y == n2.y)
            if (parent_horizontal == current_horizontal):  # if the last movement is the same as current, penalize
                extra_cost += .0001
        return 1 + extra_cost
    else:
        return math.sqrt(2)  # Note shouldn't ever actually get here because game doesn't support diagonal movement


class Node:
    '''
    For use in the shortest path A* algo
    '''
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.blocked = False
        self.parent = None
        self.travel_cost = 0

    # Need to override less than so that heapq works
    def __lt__(self, other):
        global current_end_points
        return self.get_total_cost_from_list(current_end_points) < other.get_total_cost_from_list(current_end_points)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.blocked == other.blocked and self.travel_cost == other.travel_cost and self.parent == other.parent

    def set_parent(self, parent):
        self.parent = parent
        c1 = get_travel_cost_between_nodes(self.parent, self)
        c2 = self.parent.travel_cost
        self.travel_cost = c1 + c2

    def get_heuristic_cost(self, endpoint):
        xdist = self.x - endpoint[0]
        ydist = self.y - endpoint[1]
        return math.sqrt((xdist * xdist) + (ydist * ydist))

    def get_heuristic_cost_from_list(self, endpoints):
        lowest_cost = self.get_heuristic_cost(endpoints[0])
        for i in range(1, len(endpoints)):
            cost = self.get_heuristic_cost(endpoints[i])
            if cost < lowest_cost:
                lowest_cost = cost
        return lowest_cost

    def get_total_cost_from_list(self, endpoints):
        lowest_cost = self.get_heuristic_cost_from_list(endpoints)
        return self.travel_cost + lowest_cost


class ShortestPathFinder:
    '''
    Class that is used for calculating shortest path using A*. The GameMap class has one of these classes inside it so
    don't make one of these classes yourself. Only function that you would use yourself for a algo is
    navigateMultipleEndpoints.
    So you would do game_map.shortestPathFinder.navigateMultipleEndpoints only for a algo.
    '''
    def __init__(self, game_map):
        self.game_map = game_map
        self.init_node_map()

    def init_node_map(self):
        self.node_map = []
        for x in range(self.game_map.arena_size):
            self.node_map.append([])
            for y in range(self.game_map.arena_size):
                self.node_map[x].append(Node(x, y))
                self.node_map[x][y].blocked = self.game_map.is_blocked([x, y])

    def get_neighbors(self, start, closed):
        """
        @param start - object (map?) with x, y attributes
        @param closed - list of nodes
        """
        ret = []
        for candidate_row in range(int(start.y - 1), int(start.y + 2)):
            for candidate_column in range(int(start.x - 1), int(start.x + 2)):
                row_diff = candidate_row - start.y
                col_diff = candidate_column - start.x

                row_in_bounds = candidate_row >= 0 and candidate_row < self.game_map.arena_size
                column_in_bounds = candidate_column >= 0 and candidate_column < self.game_map.arena_size
                not_diagonal = row_diff == 0 or col_diff == 0
                not_self = row_diff != 0 or col_diff != 0

                if row_in_bounds and column_in_bounds and not_diagonal and not_self:
                    if self.node_map[candidate_column][candidate_row] not in closed:
                        if not self.node_map[candidate_column][candidate_row].blocked:
                            ret.append(self.node_map[candidate_column][candidate_row])
        return ret

    def node_chain_to_locs(self, final_node):
        '''
        Takes in final node and returns list of locations to get from the start to it.
        :return: list of locations which are a list [0] = x [1] = y
        '''
        node_locations = []
        n = final_node
        while n is not None:
            node_locations.append([n.x, n.y])
            n = n.parent
        return list(reversed(node_locations))

    def get_closest_node(self, closed, end_points, player_id):
        '''
        Gets closest node to end_points in closed list
        :return:
        '''
        start_y = 0 if player_id == 1 else self.game_map.arena_size
        ret = closed[0]
        highest_y = abs(start_y - ret.y)
        for n in closed:
            node_y = abs(start_y - n.y)
            if highest_y < node_y or (node_y == highest_y and n.get_heuristic_cost_from_list(end_points) < closed[0].get_heuristic_cost_from_list(end_points)):
                highest_y = node_y
                ret = n
        return ret

    def navigate_multiple_endpoints(self, startPoint, end_points, player_id):
        '''
        :param startPoint:
        :param end_points:
        :return: list of locations from startPoint to one of end_points or the closest it can get to them. , and boolean
        for whether end point is reachable or not.
        '''
        self.init_node_map()
        global current_end_points
        current_end_points = end_points
        if len(current_end_points) < 1:
            print( "Warning: tried to find shortest path with empty list of end points", file=sys.stderr)
            return self.node_chain_to_locs(Node(startPoint[0], startPoint[1])), False

        open_list = []  # use heapq to get smallest
        closed = []

        open_list.append(self.node_map[startPoint[0]][startPoint[1]])
        current = open_list[0]

        while True:
            heapq.heapify(open_list)
            if len(open_list) > 0:
                current = heapq.heappop(open_list)
            else:
                # end_points are not reachable, return path to point as close as possible instead.
                return self.node_chain_to_locs(self.get_closest_node(closed, end_points, player_id)), False

            closed.append(current)

            end_reached = False
            for end in end_points:
                if current.x == int(end[0]) and current.y == int(end[1]):
                    end_reached = True
            # doing it grossly with break so that it avoids finishing the rest of the iteration
            if end_reached:
                break

            for n in self.get_neighbors(current, closed):
                if n in open_list:
                    new_t = current.travel_cost + get_travel_cost_between_nodes(current, n)
                    if (new_t < n.travel_cost):
                        n.set_parent(current)
                        # cost changed so need to remove and resort.
                        open_list.remove(n)
                        open_list.append(n)
                else:
                    # has no travel cost calculated yet
                    n.set_parent(current)
                    open_list.append(n)

        return self.node_chain_to_locs(current), True
