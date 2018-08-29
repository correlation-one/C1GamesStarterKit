import math
from .unit import GameUnit

class GameMap:
    def __init__(self, config):
        self.config = config
        self.arena_size = 28 
        self.half_arena = int(self.arena_size / 2)
        self.__map = self.__empty_grid()
        self.__start = [13,0]
    
    def __getitem__(self, location):
        if len(location) == 2 and self.in_arena_bounds(location):
            x,y = location
            return self.__map[x][y]
        raise InvalidCoordinate(location)

    def __setitem__(self, location, val):
        if type(location) == tuple and len(location) == 2 and self.in_arena_bounds(location):
            self.__map[location[0]][location[1]] = val
            return
        raise InvalidCoordinate(location) 

    def __iter__(self):
        self.__start = [13,0]
        return self
    
    def __next__(self):
        location = self.__start
        if location == [15,27]:
            raise StopIteration
        new_location = [location[0]+1, location[1]]
        while not self.in_arena_bounds(new_location) and not location == [14,27]:
            if new_location[0] == self.arena_size:
                new_location = [0, new_location[1]+1]
            else:
                new_location = [new_location[0]+1, new_location[1]]
        self.__start = new_location
        return location 

    def __empty_grid(self):
        grid = []
        for x in range(0, self.arena_size):
            grid.append([])
            for y in range(0, self.arena_size):
                grid[x].append([])
        return grid

    def in_arena_bounds(self, location):
        '''
        Checks if the given location is inside the diamond shaped game board.
        '''
        x, y = location
        half_board = self.half_arena

        row_size = y + 1
        startx = half_board - row_size
        endx = startx + (2 * row_size) - 1
        top_half_check = (y < self.half_arena and x >= startx and x <= endx)

        row_size = (self.arena_size - 1 - y) + 1
        startx = half_board - row_size
        endx = startx + (2 * row_size) - 1
        bottom_half_check = (y >= self.half_arena and x >= startx and x <= endx)

        return bottom_half_check or top_half_check

    def get_edge_locations(self, quadrant_description):
        '''
        Takes in an edge description and returns a list of locations.
        Valid quadrant descriptions: top_right, top_left, bottom_left, bottom_right
        '''
        edge_quadrant_indices = {
                "top_right": 0,
                "top_left": 1,
                "bottom_left": 2,
                "bottom_right": 3}
        edge_index = edge_quadrant_indices.get(quadrant_description)
        edges = self.get_edges()
        return edges[edge_index]

    def get_edges(self):
        '''
        Returns a list with four lists inside of it of locations corresponding to the four edges.
        [0] = top_right, [1] = top_left, [2] = bottom_left, [3] = bottom_right.
        '''
        top_right = []
        for num in range(0, self.half_arena):
            x = self.half_arena + num
            y = self.arena_size - 1 - num
            top_right.append([int(x), int(y)])
        top_left = []
        for num in range(0, self.half_arena):
            x = self.half_arena - 1 - num
            y = self.arena_size - 1 - num
            top_left.append([int(x), int(y)])
        bottom_left = []
        for num in range(0, self.half_arena):
            x = self.half_arena - 1 - num
            y = num
            bottom_left.append([int(x), int(y)])
        bottom_right = []
        for num in range(0, self.half_arena):
            x = self.half_arena + num
            y = num
            bottom_right.append([int(x), int(y)])
        return [top_right, top_left, bottom_left, bottom_right]
    
    def add_unit(self, unit_type, location, player_id=0):
        '''
        Add a single GameUnit to the map at the given location.
        '''
        if not self.in_arena_bounds(location):
            raise InvalidCoordinate(location)
        x, y = location
        new_unit = GameUnit(unit_type, self.config, player_id, None, "", location[0], location[1])
        if not new_unit.stationary:
            self.__map[x][y].append(new_unit)
        else:
            self.__map[x][y] = [new_unit]

    def remove_unit(self, location):
        '''
        Remove all units on the map in the given location.
        '''
        if not self.in_arena_bounds(location):
            raise InvalidCoordinate(location)
        x, y = location
        self.__map[x][y] = []

    def get_locations_in_range(self, location, radius):
        '''
        Returns locations in range of the given radius centered at the given location.
        '''
        x, y = location
        locations = []
        for i in range(int(x - radius), int(x + radius + 1)):
            for j in range(int(y - radius), int(y + radius + 1)):
                new_location = [i, j]
                # A unit with a given range affects all locations who's centers are within that range + 0.51 so we add 0.51 here
                if self.in_arena_bounds(new_location) and self.distance_between_locations(location, new_location) < radius + 0.51:
                    locations.append(new_location)
        return locations

    def distance_between_locations(self, location_1, location_2):
        '''
        Euclidean distance between two locations.
        '''
        x1, y1 = location_1
        x2, y2 = location_2

        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

class InvalidCoordinate(Exception):
    def __init__(self, location):
        super().__init__("{} is an invalid coordinate.".format(str(location)))
