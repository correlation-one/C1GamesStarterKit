import math
import copy
import sys
import json

from .navigation import ShortestPathFinder
from .util import send_command, debug_write

def empty_grid(arena_size):
    '''
    Fills in map as 3D array. Dimensions = X,Y,Array of GameUnits. GameUnit arrays are empty.
    '''
    grid = []
    for x in range(0, arena_size):
        grid.append([])
        for y in range(0, arena_size):
            grid[x].append([])
    return grid


def unit_str(unit_def):
    unit_type, x, y = unit_def
    return "{}:{},{}".format(unit_type, x, y)

def is_stationary(unit_type):
    return unit_type in TOWER_TYPES

# TODO: extract config reference from unit, can remove string generation and
# config references per unit per turn
class GameUnit:
    '''
    Class that holds information about a unit. Uses the config file. Useful for tracking what units are where on the map
    and also can be used with default parameters to check how much a unit type costs, its range etc.
    '''
    def __init__(self, unit_type, config, player_id=None, x=-1.0, y=-1.0, stability=None, gid=""):
        self.unit_type = unit_type
        self.config = config
        self.player_id = player_id
        self.x = int(x)
        self.y = int(y)
        self.gid = gid
        self.pending_removal = False
        self.__serialize_type()

        # serialize_type() must be called before we can reference config values
        # like self.max_stability
        self.stability = self.max_stability if not stability else stability

    def __serialize_type(self):
        self.stationary = is_stationary(self.unit_type)
        type_config = self.config[self.unit_type]
        if self.stationary:
            self.speed = 0
            if self.unit_type == "EI":
                self.damage = type_config["supportShieldAmount"]
            else:
                self.damage = type_config["damage"]
        else:
            self.speed = type_config["speed"]
            self.damage_t = type_config["damageT"]
            self.damage_s = type_config["damageS"]
        self.range = type_config["range"]
        self.max_stability = type_config["health"]
        self.hitbox = type_config["getHitRadius"]
        self.cost = type_config["cost"]


    # Below functions are to allow printing GameUnit easily
    def toString(self):
        return "{}{}:{}-{}-{}-{}".format(self.unit_type, "*" if self.pending_removal else "", self.x, self.y,
                                         self.stability, self.player_id)

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

class GameMap:
    '''
    This class represents a wrapper around the state of the game for the current
    turn. It has helper methods to simplify spending your resources to spawn
    units for your turn, as well as path-finding given the current state of the
    board.

    The game board is stored as: a 2 dimensional array representing each tile on
    the board. Each tile is yet another array containing the units located at
    the x,y coordinates specified in the first two indices. So getting the 2nd
    of 3 units located at (12, 13) would look like: `unit = self.map[12][13][1]`

    Path finding helpers are stored in the `shortest_path_finder` attribute.
    '''
    def __init__(self, config, serialized_string):
        self.serialized_string = serialized_string
        self.config = config

        global TOWER_TYPES
        TOWER_TYPES = ["FF", "EF", "DF"]
        self.arena_size = 28 
        self.half_arena = int(self.arena_size / 2)
        self.map = empty_grid(self.arena_size)
        self.shortest_path_finder = ShortestPathFinder(self)
        self.temp_build = []
        self.temp_deploy = []
        self.player_resources = [
                {'cores': 0, 'bits': 0},  # player 0, which is you (for now, we may be discarding this invariant soon)
                {'cores': 0, 'bits': 0}]  # player 1, which is the opponent
        self.__parse_state(serialized_string)

    def __parse_state(self, state_line):
        '''
        Fills in map based on the serialized game state so that self.map[x][y] is a list of GameUnits at the location.
        :param serialized_string:
        :return:
        '''
        state = json.loads(state_line)

        turn_info = state["turnInfo"]
        self.turn_number = int(turn_info[1])

        p1_integrity, p1_cores, p1_bits, p1_time = map(float, state["p1Stats"][:4])  # :4 in case we add more, it wont crash
        p2_integrity, p2_cores, p2_bits, p2_time = map(float, state["p2Stats"][:4])

        self.my_integrity = p1_integrity
        self.my_time = p1_time
        self.enemy_integrity = p2_integrity
        self.enemy_time = p2_time

        self.player_resources = [
            {'cores': p1_cores, 'bits': p1_bits},
            {'cores': p2_cores, 'bits': p2_bits}]

        p1units = state["p1Units"]
        p2units = state["p2Units"]

        self.__create_parsed_units(p1units, 0)
        self.__create_parsed_units(p2units, 1)

    def __create_parsed_units(self, units, player_number):
        typedef = self.config.get("typeDefinitions")
        for i, unit_types in enumerate(units):
            for uinfo in unit_types:
                unit_type = typedef[i].get("shorthand")
                sx, sy, shp, gid = uinfo[:4] # :4 in case we add more, it wont crash
                x, y = map(int, [sx, sy])                
                hp = float(shp)
                # This depends on RM always being the last unit in the string
                if unit_type == "RM":
                    self.map[x][y][0].pending_removal = True
                unit = GameUnit(unit_type, self.config, player_number, x, y, hp, gid)
                self.map[x][y].append(unit)

    def __resource_required(self, unit_type):
        return 'cores' if is_stationary(unit_type) else 'bits'

    def __set_resource(self, resource_type, new_value, player_id = 0):
        self.player_resources[player_id][resource_type] = new_value

    def __subtract_resource(self, resource_type, amount, player_id = 0):
        held_resource = self.get_resource(resource_type, player_id)
        if held_resource is None:
            err_str = "Invalid resource type passed to 'subtract_resource()': {}, {}, player_id={})"
            raise ValueError(err_str.format(resource_type, amount, player_id))
        self.__set_resource(resource_type, held_resource - amount, player_id)


    def send_messages(self):
        build_string = json.dumps(self.temp_build)
        deploy_string = json.dumps(self.temp_deploy)
        send_command(build_string)
        send_command(deploy_string)

    def get_resource(self, resource_type, player_id = 0):
        resources = self.player_resources[player_id]
        return resources.get(resource_type, None)

    def number_affordable(self, unit_type):
        cost = self.type_cost(unit_type)
        resource_type = self.__resource_required(unit_type)
        player_held = self.get_resource(resource_type)
        return math.floor(player_held / cost)

    def can_afford(self, unit_type, num=1):
        cost = self.type_cost(unit_type) * num
        resource_type = self.__resource_required(unit_type)
        player_held = self.get_resource(resource_type)
        return (player_held - cost) >= 0

    def bits_in_future(self, turns_in_future = 1, player_id = 0):
        bits  = self.get_resource('bits', player_id)

        for i in range(turns_in_future):
            bits *= (1 - self.config["foodSpoilPerRound"])
            bits += self.bits_gained_on_turn(self.turn_number + i + 1)
            bits = math.floor(bits*100)/100 #Floor to two decimal place
        return bits

    def bits_gained_on_turn(self, turn_number):
        if turn_number == 0:
            return self.config["startingFood"]
        else :
            return self.config["foodPerRound"] + (turn_number // self.config["turnIntervalForFoodSchedule"])  

    def type_cost(self, unit_type):
        unit_def = self.config.get(unit_type)
        return unit_def.get('cost')

    def number_affordable(self, unit_type):
        cost = self.type_cost(unit_type)
        resource_type = self.__resource_required(unit_type)
        player_held = self.get_resource(resource_type)
        return math.floor(player_held / cost)

    def friendly_territory(self, location):
        return location[1] < self.half_arena and self.in_arena_bounds(location)

    def can_spawn(self, unit_type, location, num=1):
        """
        Returns True if we can afford the unit, it is in bounds, on our side of
        map, it is not blocked, if it is a moving unit it is on the edge
        """
        affordable = self.can_afford(unit_type, num)
        stationary = is_stationary(unit_type)
        blocked = self.is_blocked(location) or (stationary and len(self.get_units(location)) > 0)
        on_edge = self.is_on_edge(location)
        correct_territory = self.friendly_territory(location)
        return (affordable and correct_territory and not blocked and
                (stationary or on_edge) and
                (not stationary or num == 1))

    def attempt_spawn(self, unit_type, location, num=1):
        if self.can_spawn(unit_type, location, num):
            x, y = map(int, location)
            cost = self.type_cost(unit_type) * num
            resource_type = self.__resource_required(unit_type)
            self.__subtract_resource(resource_type, cost)
            self.add_unit_to_map(unit_type, location, 1)
            if is_stationary(unit_type):
                self.temp_build.append((unit_type, x, y))
            else:
                for _ in range(num):
                    self.temp_deploy.append((unit_type, x, y))
            return True
        return False

    def attempt_remove(self, location):
        if self.friendly_territory(location) and self.is_blocked(location):
            x, y = map(int, location)
            self.temp_build.append(("RM", x, y))
            return True
        return False

    def attempt_spawn_multiple(self, unit_type, locations):
        valid_count = 0
        for location in locations:
            if self.attempt_spawn(unit_type, location):
                valid_count += 1
        return valid_count

    def attempt_remove_multiple(self, locations):
        valid_count = 0
        for location in locations:
            if self.attempt_remove(location):
                valid_count += 1
        return valid_count

    def find_path_to_edge(self, start_location, target_edge):
        '''
        The path a mobile unit will take to cross the board given the current
        map state. The path may change if the map is modified by adding
        additional firewalls. player_id is either 0 or 1. 0 for yourself 1 for
        enemy
        '''
        player_id = self.get_player_from_target_edge(target_edge)
        target_locations = [
                location for location
                in self.get_edge_locations(target_edge)
                if not self.is_blocked(location)]
        return self.shortest_path_finder.navigate_multiple_endpoints(start_location, target_locations, player_id)

    def find_path_to_location(self, start_location, target_location, player_id):
        '''
        This function is the path a unit will take to reach a specific tile given a given map state.
        Note that there is no guarentee that the unit will want to path to the provided
        '''
        return self.shortest_path_finder.navigate_multiple_endpoints(start_location, [target_location], player_id)

    def get_player_from_target_edge(self, target_edge):
        # If the unit is trying to reach a bottom edge, it is players 1s unit. Otherwise, it is player 0.
        if target_edge == "bottom_left" or target_edge == "bottom_right":
            return 1
        return 0

    def in_arena_bounds(self, location):
        """ within the diamond-shaped playable area of the arena """
        x, y = map(int, location)
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

    def contains_stationary_unit(self, location):
        """ Check if a Firewall exists at the passed location """
        x, y = map(int, location)
        for unit in self.map[x][y]:
            if unit.stationary:
                return unit
        return False

    def is_blocked(self, location):
        """ obstructed or out of bounds """
        if not self.in_arena_bounds(location):
            return True
        return self.contains_stationary_unit(location)

    def filter_blocked_locations(self, locations):
        filtered = []
        for location in locations:
            if not self.is_blocked(location):
                filtered.append(location)
        return filtered

    def is_on_edge(self, location):
        edge_locations = self.get_edges()
        for edges in edge_locations:
            if location in edges:
                return True
        return False

    def get_edge_locations(self, quadrant_description):
        edge_quadrant_indices = {
                "top_right": 0,
                "top_left": 1,
                "bottom_left": 2,
                "bottom_right": 3}
        edge_index = edge_quadrant_indices.get(quadrant_description)
        edges = self.get_edges()
        return edges[edge_index]

    def get_edges(self):
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

    def flip_over_x_axis(self, location):
        x, y = location
        return [x, self.arena_size - y - 1]

    def flip_over_y_axis(self, location):
        x, y = location
        return [self.arena_size - x - 1, y]

    def get_units(self, location):
        x, y = location
        return self.map[x][y]

    def distance_between_locations(self, location1, location2):
        x1, y1 = location1
        x2, y2 = location2

        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def get_locations_in_range(self, location, radius):
        x, y = location
        locations = []
        for i in range(int(x - radius), int(x + radius + 1)):
            for j in range(int(y - radius), int(y + radius + 1)):
                new_location = [i, j]
                # A unit with a given range affects all locations who's centers are within that range + 0.5 so we add 0.51 here
                if self.in_arena_bounds(new_location) and self.distance_between_locations(location, new_location) < radius + 0.51:
                    locations.append(new_location)
        return locations

    def get_attackers(self, location, player_id):
        attackers = []
        possible_locations= self.get_locations_in_range(location, self.config["DF"]["range"])
        for location in possible_locations:
            for unit in self.get_units(location):
                if unit.unit_type == "DF" and unit.player_id != player_id:
                    attackers.append(unit)
        return attackers

    def get_target(self, attacking_unit):
        # Target priority: Infantry > Distance > Lowest stability > Lowest y > Highest distance of x from 13.5 (The board's center)
        attacker_location = [attacking_unit.x, attacking_unit.y]
        possible_locations = self.get_locations_in_range(attacker_location, attacking_unit.range)
        target = None
        target_stationary = True
        target_distance = sys.maxsize
        target_stability = sys.maxsize
        target_y = self.arena_size
        target_x_distance = 0

        for location in possible_locations:
            for unit in self.get_units(location):
                if unit.player_id == attacking_unit.player_id or (attacking_unit.unit_type == "SI" and is_stationary(unit)):
                    continue

                new_target = False
                unit_stationary = unit.stationary
                unit_distance = self.distance_between_locations(location, [attacking_unit.x, attacking_unit.y])
                unit_stability = unit.stability
                unit_y = unit.y
                unit_x_distance = abs(self.half_arena - 0.5 - unit.x)

                if target_stationary and not unit_stationary:
                    new_target = True
                elif not target_stationary and unit_stationary:
                    continue
                
                if target_distance > unit_distance:
                    new_target = True
                elif target_distance < unit_distance and not new_target:
                    continue

                if target_stability > unit_stability:
                    new_target = True
                elif target_stability < unit_stability and not new_target:
                    continue

                if target_y > unit_y:
                    new_target = True
                elif target_y < unit_y and not new_target:
                    continue       

                if target_x_distance < unit_x_distance:
                    new_target = True
                
                if new_target:
                    target = unit
                    target_stationary = unit_stationary
                    target_distance = unit_distance
                    target_stability = unit_stability
                    target_y = unit_y
                    target_x_distance = unit_x_distance
        return target

    # Map delta is a list of changes. Each change is in the form ["UnitString", [x , y]]
    def get_map_copy(self, map_delta = None):
        map_copy = copy.deepcopy(self)
        if map_delta is None:
            return map_copy
        for change in map_delta:
            map_copy.add_unit_to_map(change[0], change[1])
        return map_copy

    # This function is most useful for creating hypothetical gamestates in copies of game map
    def add_unit_to_map(self, unit_type, location, player_id=0):
        x, y = location
        new_unit = GameUnit(unit_type, self.config, player_id, x, y)
        if len(self.map[x][y]) > 0 and not new_unit.stationary:
            if not is_stationary(self.map[x][y][0].unit_type): 
                self.map[x][y].append(new_unit)
            else:
                self.map[x][y] = [new_unit]
        else:
            self.map[x][y] = [new_unit]

    def clear_units_from_map_location(self, location):
        x, y = location
        self.map[x][y] = []
