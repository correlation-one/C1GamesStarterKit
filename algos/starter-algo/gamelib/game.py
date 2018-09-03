import math
import json

from .navigation import ShortestPathFinder
from .util import send_command, debug_write
from .unit import GameUnit
from .map import GameMap

def is_stationary(unit_type):
    return unit_type in FIREWALL_TYPES

class GameState:
    '''
    This class represents the state of the game for the current turn. 
    It has helper methods to simplify spending your resources to spawn
    units for your turn, as well as path-finding given the current state of the
    board.

    The game board is stored as: a 2 dimensional array representing each tile on
    the board. Each tile is yet another array containing the units located at
    the x,y coordinates specified in the first two indices. So getting the 2nd
    of 3 units located at (12, 13) would look like: `unit = self.game_map[12,13][1]`

    Path finding helpers are stored in the `shortest_path_finder` attribute.
    '''
    def __init__(self, config, serialized_string):
        self.serialized_string = serialized_string
        self.config = config

        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, REMOVE, FIREWALL_TYPES, UNIT_TYPE_TO_INDEX
        UNIT_TYPE_TO_INDEX = {}
        FILTER = config["unitInformation"][0]["shorthand"]
        UNIT_TYPE_TO_INDEX[FILTER] = 0
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        UNIT_TYPE_TO_INDEX[ENCRYPTOR] = 1
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        UNIT_TYPE_TO_INDEX[DESTRUCTOR] = 2
        PING = config["unitInformation"][3]["shorthand"]
        UNIT_TYPE_TO_INDEX[PING] = 3
        EMP = config["unitInformation"][4]["shorthand"]
        UNIT_TYPE_TO_INDEX[EMP] = 4
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        UNIT_TYPE_TO_INDEX[SCRAMBLER] = 5
        REMOVE = config["unitInformation"][6]["shorthand"]
        UNIT_TYPE_TO_INDEX[REMOVE] = 6
        
        FIREWALL_TYPES = [FILTER, ENCRYPTOR, DESTRUCTOR]

        self.ARENA_SIZE = 28
        self.HALF_ARENA = int(self.ARENA_SIZE / 2)
        self.BITS = 0
        self.CORES = 1

        self.game_map = GameMap(self.config)
        self.shortest_path_finder = ShortestPathFinder()
        self.build_stack = []
        self.deploy_stack = []
        self.player_resources = [
                {'cores': 0, 'bits': 0},  # player 0, which is you
                {'cores': 0, 'bits': 0}]  # player 1, which is the opponent
        self.__parse_state(serialized_string)

    def __parse_state(self, state_line):
        '''
        Fills in map based on the serialized game state so that self.game_map[x,y] is a list of GameUnits at that location.
        state_line is the game state as a json string.
        '''
        state = json.loads(state_line)

        turn_info = state["turnInfo"]
        self.turn_number = int(turn_info[1])

        p1_health, p1_cores, p1_bits, p1_time = map(float, state["p1Stats"][:4])
        p2_health, p2_cores, p2_bits, p2_time = map(float, state["p2Stats"][:4])

        self.my_health = p1_health
        self.my_time = p1_time
        self.enemy_health = p2_health
        self.enemy_time = p2_time

        self.player_resources = [
            {'cores': p1_cores, 'bits': p1_bits},
            {'cores': p2_cores, 'bits': p2_bits}]

        p1units = state["p1Units"]
        p2units = state["p2Units"]

        self.__create_parsed_units(p1units, 0)
        self.__create_parsed_units(p2units, 1)

    def __create_parsed_units(self, units, player_number):
        '''
        Helper function for __parse_state to add units to the map.
        '''
        typedef = self.config.get("unitInformation")
        for i, unit_types in enumerate(units):
            for uinfo in unit_types:
                unit_type = typedef[i].get("shorthand")
                sx, sy, shp, unit_id = uinfo[:4]
                x, y = map(int, [sx, sy])
                hp = float(shp)
                # This depends on RM always being the last type to be processed
                if unit_type == REMOVE:
                    self.game_map[x,y][0].pending_removal = True
                unit = GameUnit(unit_type, self.config, player_number, hp, unit_id, x, y)
                self.game_map[x,y].append(unit)

    def __resource_required(self, unit_type):
        return self.CORES if is_stationary(unit_type) else self.BITS

    def __set_resource(self, resource_type, amount, player_index=0):
        '''
        Sets the resources for the given player_index and resource_type.
        Is automatically called by other provided functions. 
        '''
        if resource_type == self.BITS:
            resource_key = 'bits'
        elif resource_type == self.CORES:
            resource_key = 'cores'
        held_resource = self.get_resource(resource_type, player_index)
        self.player_resources[player_index][resource_key] = held_resource + amount

    def submit_turn(self):
        '''
        Sends build message to the game. 
        Must be called at the end of the algo_strategy step function or the algo will hang.
        '''
        build_string = json.dumps(self.build_stack)
        deploy_string = json.dumps(self.deploy_stack)
        send_command(build_string)
        send_command(deploy_string)

    def get_resource(self, resource_type, player_index = 0):
        '''
        Returns number of given resource_type given player_index has.
        Parameter resource_type must be cores or bits.
        Parameter player_index must be 0 or 1, 0 for yourself 1 for enemy.
        '''
        if resource_type == self.BITS:
            resource_key = 'bits'
        elif resource_type == self.CORES:
            resource_key = 'cores'
        resources = self.player_resources[player_index]
        return resources.get(resource_key, None)

    def number_affordable(self, unit_type):
        '''
        Returns the number of units affordable of the given unit_type.
        '''
        cost = self.type_cost(unit_type)
        resource_type = self.__resource_required(unit_type)
        player_held = self.get_resource(resource_type)
        return math.floor(player_held / cost)

    def project_future_bits(self, turns_in_future=1, player_index=0, current_bits=None):
        '''
        Returns number of bits stored after the given number of turns, assuming we start with the bits currently 
        held by the player corresponding to player_index or starting from current_bits instead if it is provided. 
        '''
        bits = self.get_resource(self.BITS, player_index) if not current_bits else current_bits
        for increment in range(1, turns_in_future + 1):
            current_turn = self.turn_number + increment
            bits *= (1 - self.config["resources"]["bitDecayPerRound"])
            bits_gained = self.config["resources"]["bitsPerRound"] + (current_turn // self.config["resources"]["turnIntervalForBitSchedule"])
            bits += bits_gained
            bits = math.floor(bits * 100) / 100
        return bits

    def type_cost(self, unit_type):
        '''
        Returns cost to spawn for the given unit_type.
        '''
        unit_def = self.config["unitInformation"][UNIT_TYPE_TO_INDEX[unit_type]]
        return unit_def.get('cost')

    def can_spawn(self, unit_type, location, num=1):
        """
        Returns True if we can afford the unit, it is in bounds, on our side of
        map, it is not blocked, and if it is a moving unit it is on our edges.
        """
        affordable = self.number_affordable(unit_type) >= num
        stationary = is_stationary(unit_type)
        blocked = self.contains_stationary_unit(location) or (stationary and len(self.game_map[location[0],location[1]]) > 0)
        correct_territory = location[1] < self.HALF_ARENA
        on_edge = location in (self.game_map.get_edge_locations(self.game_map.BOTTOM_LEFT) + self.game_map.get_edge_locations(self.game_map.BOTTOM_RIGHT))

        return (affordable and correct_territory and not blocked and
                (stationary or on_edge) and
                (not stationary or num == 1))

    def attempt_spawn(self, unit_type, locations, num=1):
        '''
        Attempts to spawn new units with the type given in the given locations.
        Will accept both a single location and a list of locations. Optional parameter
        num allows spawning multiple units per location.
        If a single location is invalid or not enough resources, will still spawn
        the units in the list that it can.
        Returns number of units successfully spawned.
        '''
        if type(locations[0]) == int:
            locations = [locations]
        spawned_units = 0
        for location in locations:
            for _ in range(num):
                if self.can_spawn(unit_type, location):
                    x, y = map(int, location)
                    cost = self.type_cost(unit_type)
                    resource_type = self.__resource_required(unit_type)
                    self.__set_resource(resource_type, -cost)
                    self.game_map.add_unit(unit_type, location, 0)
                    if is_stationary(unit_type):
                        self.build_stack.append((unit_type, x, y))
                    else:
                        self.deploy_stack.append((unit_type, x, y))
                    spawned_units += 1
        return spawned_units

    def attempt_remove(self, locations):
        '''
        Attempts to remove existing friendly firewalls in the given locations.
        Will accept both a single location and a list of locations.
        If a some locations are invalid will still attempt to remove the rest.
        Returns number of units successfully removed.
        '''
        if type(locations[0]) == int:
            locations = [locations]
        removed_units = 0
        for location in locations:
            if location[1] < self.HALF_ARENA and self.contains_stationary_unit(location):
                x, y = map(int, location)
                removed_unit = self.game_map[x,y][0]
                self.build_stack.append((REMOVE, x, y))
                resource_type = self.__resource_required(removed_unit)
                refund = self.type_cost(removed_unit.unit_type) * self.config["mechanics"]["destroyOwnUnitRefund"] * (removed_unit.stability / removed_unit.max_stability)
                self.__set_resource(resource_type, refund)
                removed_units += 1
        return removed_units

    def find_path_to_edge(self, start_location, target_edge):
        '''
        The path a mobile unit will take to cross the board with the current
        map state. The path may change if the map is modified by adding
        additional firewalls after this turn by the enemy player.
        '''
        end_points = self.game_map.get_edge_locations(target_edge)
        self.shortest_path_finder.navigate_multiple_endpoints(start_location, end_points, self)

    def contains_stationary_unit(self, location):
        """ Check if a Firewall exists at the given location. """
        x, y = map(int, location)
        for unit in self.game_map[x,y]:
            if unit.stationary:
                return unit
        return False
