import math
import json
import warnings

from .navigation import ShortestPathFinder
from .util import send_command, debug_write
from .unit import GameUnit
from .game_map import GameMap

def is_stationary(unit_type):
    return unit_type in FIREWALL_TYPES

class GameState:
    """Represents the entire gamestate for a given turn
    Provides methods related to resources and unit deployment

    Attributes:
        * UNIT_TYPE_TO_INDEX (dict): Maps a unit to a corresponding index
        * FILTER (str): A constant representing the filter unit
        * ENCRYPTOR (str): A constant representing the encryptor unit
        * DESTRUCTOR (str): A constant representing the destructor unit
        * PING (str): A constant representing the ping unit
        * EMP (str): A constant representing the emp unit
        * SCRAMBLER (str): A constant representing the scrambler unit
        * FIREWALL_TYPES (list): A list of the firewall units

        * ARENA_SIZE (int): The size of the arena
        * HALF_ARENA (int): Half the size of the arena
        * BITS (int): A constant representing the bits resource
        * CORES (int): A constant representing the cores resource
         
        * game_map (:obj: GameMap): The current GameMap
        * turn_number (int): The current turn number. Starts at 0.
        * my_health (int): Your current remaining health
        * my_time (int): The time you took to submit your previous turn
        * enemy_health (int): Your opponents current remaining health
        * enemy_time (int): Your opponents current remaining time
    """

    def __init__(self, config, serialized_string):
        """ Setup a turns variables using arguments passed

        Args:
            * config (JSON): A json object containing information about the game
            * serialized_string (string): A string containing information about the game state at the start of this turn

        """
        self.serialized_string = serialized_string
        self.config = config

        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, REMOVE, FIREWALL_TYPES, ALL_UNITS, UNIT_TYPE_TO_INDEX
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

        ALL_UNITS = [PING, EMP, SCRAMBLER, FILTER, ENCRYPTOR, DESTRUCTOR]
        FIREWALL_TYPES = [FILTER, ENCRYPTOR, DESTRUCTOR]

        self.ARENA_SIZE = 28
        self.HALF_ARENA = int(self.ARENA_SIZE / 2)
        self.BITS = 0
        self.CORES = 1

        self.game_map = GameMap(self.config)
        self._shortest_path_finder = ShortestPathFinder()
        self._build_stack = []
        self._deploy_stack = []
        self._player_resources = [
                {'cores': 0, 'bits': 0},  # player 0, which is you
                {'cores': 0, 'bits': 0}]  # player 1, which is the opponent
        self.__parse_state(serialized_string)

    def __parse_state(self, state_line):
        """
        Fills in map based on the serialized game state so that self.game_map[x,y] is a list of GameUnits at that location.
        state_line is the game state as a json string.
        """
        state = json.loads(state_line)

        turn_info = state["turnInfo"]
        self.turn_number = int(turn_info[1])

        p1_health, p1_cores, p1_bits, p1_time = map(float, state["p1Stats"][:4])
        p2_health, p2_cores, p2_bits, p2_time = map(float, state["p2Stats"][:4])

        self.my_health = p1_health
        self.my_time = p1_time
        self.enemy_health = p2_health
        self.enemy_time = p2_time

        self._player_resources = [
            {'cores': p1_cores, 'bits': p1_bits},
            {'cores': p2_cores, 'bits': p2_bits}]

        p1units = state["p1Units"]
        p2units = state["p2Units"]

        self.__create_parsed_units(p1units, 0)
        self.__create_parsed_units(p2units, 1)

    def __create_parsed_units(self, units, player_number):
        """
        Helper function for __parse_state to add units to the map.
        """
        typedef = self.config.get("unitInformation")
        for i, unit_types in enumerate(units):
            for uinfo in unit_types:
                unit_type = typedef[i].get("shorthand")
                sx, sy, shp = uinfo[:3]
                x, y = map(int, [sx, sy])
                hp = float(shp)
                # This depends on RM always being the last type to be processed
                if unit_type == REMOVE:
                    self.game_map[x,y][0].pending_removal = True
                unit = GameUnit(unit_type, self.config, player_number, hp, x, y)
                self.game_map[x,y].append(unit)

    def __resource_required(self, unit_type):
        return self.CORES if is_stationary(unit_type) else self.BITS

    def __set_resource(self, resource_type, amount, player_index=0):
        """
        Sets the resources for the given player_index and resource_type.
        Is automatically called by other provided functions. 
        """
        if resource_type == self.BITS:
            resource_key = 'bits'
        elif resource_type == self.CORES:
            resource_key = 'cores'
        held_resource = self.get_resource(resource_type, player_index)
        self._player_resources[player_index][resource_key] = held_resource + amount

    def _invalid_player_index(self, index):
        warnings.warn("Invalid player index {} passed, player index should always be 0 (yourself) or 1 (your opponent)".format(index))
    
    def _invalid_unit(self, unit):
        warnings.warn("Invalid unit {}".format(unit))

    def submit_turn(self):
        """Submit and end your turn.
        Must be called at the end of your turn or the algo will hang.
        
        """
        build_string = json.dumps(self._build_stack)
        deploy_string = json.dumps(self._deploy_stack)
        send_command(build_string)
        send_command(deploy_string)

    def get_resource(self, resource_type, player_index = 0):
        """Gets a players resources

        Args:
            * resource_type: self.CORES or self.BITS
            * player_index: The index corresponding to the player whos resources you are querying, 0 for you 1 for the enemy

        Returns:
            The number of the given resource the given player controls

        """
        if not player_index == 1 and not player_index == 0:
            self._invalid_player_index(player_index)
        if not resource_type == self.BITS and not resource_type == self.CORES:
            warnings.warn("Invalid resource_type '{}'. Please use game_state.BITS or game_state.CORES".format(resource_type))

        if resource_type == self.BITS:
            resource_key = 'bits'
        elif resource_type == self.CORES:
            resource_key = 'cores'
        resources = self._player_resources[player_index]
        return resources.get(resource_key, None)

    def number_affordable(self, unit_type):
        """The number of units of a given type we can afford

        Args:
            * unit_type: A unit type, PING, FILTER, etc.

        Returns:
            The number of units affordable of the given unit_type.

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return

        cost = self.type_cost(unit_type)
        resource_type = self.__resource_required(unit_type)
        player_held = self.get_resource(resource_type)
        return math.floor(player_held / cost)

    def project_future_bits(self, turns_in_future=1, player_index=0, current_bits=None):
        """Predicts the number of bits we will have on a future turn

        Args:
            * turns_in_future: The number of turns in the future we want to look forward to predict
            * player_index: The player whos bits we are tracking
            * current_bits: If we pass a value here, we will use that value instead of the current bits of the given player.

        Returns:
            The number of bits the given player will have after the given number of turns

        """

        if turns_in_future < 1 or turns_in_future > 99:
            warnings.warn("Invalid turns in future used ({}). Turns in future should be between 1 and 99".format(turns_in_future))
        if not player_index == 1 and not player_index == 0:
            self._invalid_player_index(player_index)
        if type(current_bits) == int and current_bits < 0:
            warnings.warn("Invalid current bits ({}). Current bits cannot be negative.".format(current_bits))

        bits = self.get_resource(self.BITS, player_index) if not current_bits else current_bits
        for increment in range(1, turns_in_future + 1):
            current_turn = self.turn_number + increment
            bits *= (1 - self.config["resources"]["bitDecayPerRound"])
            bits_gained = self.config["resources"]["bitsPerRound"] + (current_turn // self.config["resources"]["turnIntervalForBitSchedule"])
            bits += bits_gained
            bits = round(bits, 1)
        return bits

    def type_cost(self, unit_type):
        """Gets the cost of a unit based on its type

        Args:
            * unit_type: The units type

        Returns:
            The units cost

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return

        unit_def = self.config["unitInformation"][UNIT_TYPE_TO_INDEX[unit_type]]
        return unit_def.get('cost')

    def can_spawn(self, unit_type, location, num=1):
        """Check if we can spawn a unit at a location. 

        To units, we need to be able to afford them, and the location must be
        in bounds, unblocked, on our side of the map, not on top of a unit we can't stack with, 
        and on an edge if the unit is information.

        Args:
            * unit_type: The type of the unit
            * location: The location we want to spawn the unit
            * num: The number of units we want to spawn

        Returns:
            True if we can spawn the unit(s)

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return
        
        if not self.game_map.in_arena_bounds(location):
            return False

        affordable = self.number_affordable(unit_type) >= num
        stationary = is_stationary(unit_type)
        blocked = self.contains_stationary_unit(location) or (stationary and len(self.game_map[location[0],location[1]]) > 0)
        correct_territory = location[1] < self.HALF_ARENA
        on_edge = location in (self.game_map.get_edge_locations(self.game_map.BOTTOM_LEFT) + self.game_map.get_edge_locations(self.game_map.BOTTOM_RIGHT))

        return (affordable and correct_territory and not blocked and
                (stationary or on_edge) and
                (not stationary or num == 1))

    def attempt_spawn(self, unit_type, locations, num=1):
        """Attempts to spawn new units with the type given in the given locations.

        Args:
            * unit_type: The type of unit we want to spawn
            * locations: A single location or list of locations to spawn units at
            * num: The number of units of unit_type to deploy at the given location(s)

        Returns:
            The number of units successfully spawned

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return
        if num < 1:
            warnings.warn("Attempted to spawn fewer than one units! ({})".format(num))
            return
      
        if type(locations[0]) == int:
            locations = [locations]
        spawned_units = 0
        for location in locations:
            for i in range(num):
                if self.can_spawn(unit_type, location):
                    x, y = map(int, location)
                    cost = self.type_cost(unit_type)
                    resource_type = self.__resource_required(unit_type)
                    self.__set_resource(resource_type, 0 - cost)
                    self.game_map.add_unit(unit_type, location, 0)
                    if is_stationary(unit_type):
                        self._build_stack.append((unit_type, x, y))
                    else:
                        self._deploy_stack.append((unit_type, x, y))
                    spawned_units += 1
                else:
                    warnings.warn("Could not spawn {} number {} at location {}. Location is blocked, invalid, or you don't have enough resources.".format(unit_type, i, location))
        return spawned_units

    def attempt_remove(self, locations):
        """Attempts to remove existing friendly firewalls in the given locations.

        Args:
            * locations: A location or list of locations we want to remove firewalls from

        Returns:
            The number of firewalls successfully flagged for removal

        """
        if type(locations[0]) == int:
            locations = [locations]
        removed_units = 0
        for location in locations:
            if location[1] < self.HALF_ARENA and self.contains_stationary_unit(location):
                x, y = map(int, location)
                self._build_stack.append((REMOVE, x, y))
                removed_units += 1
            else:
                warnings.warn("Could not remove a unit from {}. Location has no firewall or is enemy territory.".format(location))
        return removed_units

    def find_path_to_edge(self, start_location, target_edge):
        """Gets the path a unit at a given location would take

        Args:
            * start_location: The location of a hypothetical unit
            * target_edge: The edge the unit wants to reach. game_map.TOP_LEFT, game_map.BOTTOM_RIGHT, etc.

        Returns:
            A list of locations corresponding to the path the unit would take 
            to get from it's starting location to the best available end location

        """
        if self.contains_stationary_unit(start_location):
            warnings.warn("Attempted to perform pathing from blocked starting location {}".format(start_location))
            return
        end_points = self.game_map.get_edge_locations(target_edge)
        return self._shortest_path_finder.navigate_multiple_endpoints(start_location, end_points, self)

    def contains_stationary_unit(self, location):
        """Check if a location is blocked

        Args:
            * location: The location to check

        Returns:
            True if there is a stationary unit at the location, False otherwise
        """
        x, y = map(int, location)
        for unit in self.game_map[x,y]:
            if unit.stationary:
                return unit
        return False

    def suppress_warnings(self, suppress):
        """Suppress all warnings

        Args: 
            * suppress: If true, disable warnings. If false, enable warnings.
        """

        if suppress:
            warnings.filterwarnings("ignore")
        else:
            warnings.resetwarnings()

