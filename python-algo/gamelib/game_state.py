import math
import json
import sys

from .navigation import ShortestPathFinder
from .util import send_command, debug_write
from .unit import GameUnit
from .game_map import GameMap

def is_stationary(unit_type):
    """
        Args:
            unit_type: A unit type
        
        Returns: 
            Boolean, True if the unit is stationary, False otherwise.
    """
    return unit_type in STRUCTURE_TYPES

class GameState:
    """Represents the entire gamestate for a given turn
    Provides methods related to resources and unit deployment

    Attributes :
        * UNIT_TYPE_TO_INDEX (dict): Maps a unit to a corresponding index
        * WALL (str): A constant representing the wall unit
        * SUPPORT (str): A constant representing the support unit
        * TURRET (str): A constant representing the turret unit
        * SCOUT (str): A constant representing the scout unit
        * DEMOLISHER (str): A constant representing the demolisher unit
        * INTERCEPTOR (str): A constant representing the interceptor unit
        * REMOVE (str): A constant representing removing your own unit
        * UPGRADE (str): A constant representing upgrading a unit
        * STRUCTURE_TYPES (list): A list of the structure units

        * ARENA_SIZE (int): The size of the arena
        * HALF_ARENA (int): Half the size of the arena
        * MP (int): A constant representing the Mobile Points resource, used in the get_resource function
        * SP (int): A constant representing the SP resource, used in the get_resource function
         
        * game_map (:obj: GameMap): The current GameMap. To retrieve a list of GameUnits at a location, use game_map[x, y]
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
        self.enable_warnings = True

        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE, STRUCTURE_TYPES, ALL_UNITS, UNIT_TYPE_TO_INDEX
        UNIT_TYPE_TO_INDEX = {}
        WALL = config["unitInformation"][0]["shorthand"]
        UNIT_TYPE_TO_INDEX[WALL] = 0
        SUPPORT = config["unitInformation"][1]["shorthand"]
        UNIT_TYPE_TO_INDEX[SUPPORT] = 1
        TURRET = config["unitInformation"][2]["shorthand"]
        UNIT_TYPE_TO_INDEX[TURRET] = 2
        SCOUT = config["unitInformation"][3]["shorthand"]
        UNIT_TYPE_TO_INDEX[SCOUT] = 3
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        UNIT_TYPE_TO_INDEX[DEMOLISHER] = 4
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        UNIT_TYPE_TO_INDEX[INTERCEPTOR] = 5
        REMOVE = config["unitInformation"][6]["shorthand"]
        UNIT_TYPE_TO_INDEX[REMOVE] = 6
        UPGRADE = config["unitInformation"][7]["shorthand"]
        UNIT_TYPE_TO_INDEX[UPGRADE] = 7

        ALL_UNITS = [SCOUT, DEMOLISHER, INTERCEPTOR, WALL, SUPPORT, TURRET]
        STRUCTURE_TYPES = [WALL, SUPPORT, TURRET]

        self.ARENA_SIZE = 28
        self.HALF_ARENA = int(self.ARENA_SIZE / 2)
        self.MP = 1
        self.SP = 0
        global MP, SP
        MP = self.MP
        SP = self.SP

        self.game_map = GameMap(self.config)
        self._shortest_path_finder = ShortestPathFinder()
        self._build_stack = []
        self._deploy_stack = []
        self._player_resources = [
                {'SP': 0, 'MP': 0},  # player 0, which is you
                {'SP': 0, 'MP': 0}]  # player 1, which is the opponent
        self.__parse_state(serialized_string)

    def __parse_state(self, state_line):
        """
        Fills in map based on the serialized game state so that self.game_map[x,y] is a list of GameUnits at that location.
        state_line is the game state as a json string.
        """
        state = json.loads(state_line)

        turn_info = state["turnInfo"]
        self.turn_number = int(turn_info[1])

        p1_health, p1_SP, p1_MP, p1_time = map(float, state["p1Stats"][:4])
        p2_health, p2_SP, p2_MP, p2_time = map(float, state["p2Stats"][:4])

        self.my_health = p1_health
        self.my_time = p1_time
        self.enemy_health = p2_health
        self.enemy_time = p2_time

        self._player_resources = [
            {'SP': p1_SP, 'MP': p1_MP},
            {'SP': p2_SP, 'MP': p2_MP}]

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
                # This depends on RM and UP always being the last types to be processed
                if unit_type == REMOVE:
                    # Quick fix will deploy engine fix soon
                    if self.contains_stationary_unit([x,y]):
                        self.game_map[x,y][0].pending_removal = True
                elif unit_type == UPGRADE:
                    if self.contains_stationary_unit([x,y]):
                        self.game_map[x,y][0].upgrade()
                else:
                    unit = GameUnit(unit_type, self.config, player_number, hp, x, y)
                    self.game_map[x,y].append(unit)

    def __resource_required(self, unit_type):
        return self.SP if is_stationary(unit_type) else self.MP

    def __set_resource(self, resource_type, amount, player_index=0):
        """
        Sets the resources for the given player_index and resource_type.
        Is automatically called by other provided functions.
        Adds the value amount to the current held resources
        """
        if resource_type == self.MP:
            resource_key = 'MP'
        elif resource_type == self.SP:
            resource_key = 'SP'
        held_resource = self.get_resource(resource_type, player_index)
        self._player_resources[player_index][resource_key] = held_resource + amount

    def _invalid_player_index(self, index):
        self.warn("Invalid player index {} passed, player index should always be 0 (yourself) or 1 (your opponent)".format(index))
    
    def _invalid_unit(self, unit):
        self.warn("Invalid unit {}".format(unit))

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
            resource_type: MP (1) or SP (0)
            player_index: The index corresponding to the player whos resources you are querying, 0 for you 1 for the enemy

        Returns:
            The number of the given resource the given player controls

        """
        if not player_index == 1 and not player_index == 0:
            self._invalid_player_index(player_index)
            return
        if not resource_type == self.MP and not resource_type == self.SP:
            self.warn("Invalid resource_type '{}'. Please use MP (0) or SP (1)".format(resource_type))
            return

        if resource_type == self.MP:
            resource_key = 'MP'
        elif resource_type == self.SP:
            resource_key = 'SP'
        resources = self._player_resources[player_index]
        return resources.get(resource_key, None)

    def get_resources(self, player_index = 0):
        """Gets a players resources as a list

        Args:
            player_index: The index corresponding to the player whos resources you are querying, 0 for you 1 for the enemy

        Returns:
            [Float, Float] list where the first entry is SP the second is MP

        """
        if not player_index == 1 and not player_index == 0:
            self._invalid_player_index(player_index)
            return

        resource_key1 = 'SP'
        resource_key2 = 'MP'
        resources = self._player_resources[player_index]
        return [resources.get(resource_key1, None), resources.get(resource_key2, None)]

    def number_affordable(self, unit_type):
        """The number of units of a given type we can afford

        Args:
            unit_type: A unit type, SCOUT, WALL, etc.

        Returns:
            The number of units affordable of the given unit_type.

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return

        costs = self.type_cost(unit_type)
        player_held = self.get_resources()
        if costs[MP] > 0 and costs[SP] > 0:
            return min(math.floor(player_held[SP] / costs[SP]), math.floor(player_held[MP] / costs[MP]))
        elif costs[MP] > 0:
            return math.floor(player_held[MP] / costs[MP])
        elif costs[SP] > 0:
            return math.floor(player_held[SP] / costs[SP])
        else:
            self.warn("Invalid costs for unit, cost is 0 for both resources, returning 0")
            return 0

    def project_future_MP(self, turns_in_future=1, player_index=0, current_MP=None):
        """Predicts the number of MP we will have on a future turn

        Args:
            turns_in_future: The number of turns in the future we want to look forward to predict
            player_index: The player whose MP we are tracking
            current_MP: If we pass a value here, we will use that value instead of the current MP of the given player.

        Returns:
            The number of MP the given player will have after the given number of turns

        """

        if turns_in_future < 1 or turns_in_future > 99:
            self.warn("Invalid turns in future used ({}). Turns in future should be between 1 and 99".format(turns_in_future))
        if not player_index == 1 and not player_index == 0:
            self._invalid_player_index(player_index)
        if type(current_MP) == int and current_MP < 0:
            self.warn("Invalid current MP ({}). Current MP cannot be negative.".format(current_MP))

        MP = self.get_resource(self.MP, player_index) if not current_MP else current_MP
        for increment in range(1, turns_in_future + 1):
            current_turn = self.turn_number + increment
            MP *= (1 - self.config["resources"]["bitDecayPerRound"])
            MP_per_round = self.config["resources"]["bitsPerRound"]
            MP_ramp_ups = current_turn // self.config["resources"]["turnIntervalForBitSchedule"]
            MP_per_round_growth = self.config["resources"]["bitGrowthRate"]
            MP_gained = MP_per_round + (MP_per_round_growth * MP_ramp_ups)
            MP += MP_gained
            MP = round(MP, 1)
        return MP

    def type_cost(self, unit_type, upgrade=False):
        """Gets the cost of a unit based on its type

        Args:
            unit_type: The units type (string shorthand)

        Returns:
            The units costs as a list [SP, MP]

        """
        if unit_type == REMOVE:
            self._invalid_unit(unit_type)
            return
        
        unit_def = self.config["unitInformation"][UNIT_TYPE_TO_INDEX[unit_type]]
        cost_base = [unit_def.get('cost1', 0), unit_def.get('cost2', 0)]
        if upgrade:
            return [unit_def.get('upgrade', {}).get('cost1', cost_base[SP]), unit_def.get('upgrade', {}).get('cost2', cost_base[MP])]

        return cost_base


    def can_spawn(self, unit_type, location, num=1):
        """Check if we can spawn a unit at a location. 

        To units, we need to be able to afford them, and the location must be
        in bounds, unblocked, on our side of the map, not on top of a unit we can't stack with, 
        and on an edge if the unit is mobile.

        Args:
            unit_type: The type of the unit
            location: The location we want to spawn the unit
            num: The number of units we want to spawn

        Returns:
            True if we can spawn the unit(s)

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return
        
        if not self.game_map.in_arena_bounds(location):
            if self.enable_warnings:
                self.warn("Could not spawn {} at location {}. Location invalid.".format(unit_type, location))
            return False

        affordable = self.number_affordable(unit_type) >= num
        stationary = is_stationary(unit_type)
        blocked = self.contains_stationary_unit(location) or (stationary and len(self.game_map[location[0],location[1]]) > 0)
        correct_territory = location[1] < self.HALF_ARENA
        on_edge = location in (self.game_map.get_edge_locations(self.game_map.BOTTOM_LEFT) + self.game_map.get_edge_locations(self.game_map.BOTTOM_RIGHT))

        if self.enable_warnings:
            fail_reason = ""
            if not affordable:
                fail_reason = fail_reason + " Not enough resources."
            if blocked:
                fail_reason = fail_reason + " Location is blocked."
            if not correct_territory:
                fail_reason = fail_reason + " Location in enemy territory."
            if not (stationary or on_edge):
                fail_reason = fail_reason + " Information units must be deployed on the edge."
            if len(fail_reason) > 0:
                self.warn("Could not spawn {} at location {}.{}".format(unit_type, location, fail_reason))

        return (affordable and correct_territory and not blocked and
                (stationary or on_edge) and
                (not stationary or num == 1))

    def attempt_spawn(self, unit_type, locations, num=1):
        """Attempts to spawn new units with the type given in the given locations.

        Args:
            unit_type: The type of unit we want to spawn
            locations: A single location or list of locations to spawn units at
            num: The number of units of unit_type to deploy at the given location(s)

        Returns:
            The number of units successfully spawned

        """
        if unit_type not in ALL_UNITS:
            self._invalid_unit(unit_type)
            return
        if num < 1:
            self.warn("Attempted to spawn fewer than one units! ({})".format(num))
            return
      
        if type(locations[0]) == int:
            locations = [locations]
        spawned_units = 0
        for location in locations:
            for i in range(num):
                if self.can_spawn(unit_type, location, 1):
                    x, y = map(int, location)
                    costs = self.type_cost(unit_type)
                    self.__set_resource(SP, 0 - costs[SP])
                    self.__set_resource(MP, 0 - costs[MP])
                    self.game_map.add_unit(unit_type, location, 0)
                    if is_stationary(unit_type):
                        self._build_stack.append((unit_type, x, y))
                    else:
                        self._deploy_stack.append((unit_type, x, y))
                    spawned_units += 1
                else:
                    break
        return spawned_units

    def attempt_remove(self, locations):
        """Attempts to remove existing friendly structures in the given locations.

        Args:
            locations: A location or list of locations we want to remove structures from

        Returns:
            The number of structures successfully flagged for removal

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
                self.warn("Could not remove a unit from {}. Location has no structures or is enemy territory.".format(location))
        return removed_units

    def attempt_upgrade(self, locations):
        """Attempts to upgrade units in the given locations.

        Args:
            locations: A single location or list of locations to upgrade units at

        Returns:
            The number of units successfully upgraded

        """

        if type(locations[0]) == int:
            locations = [locations]
        spawned_units = 0
        for location in locations:
            if location[1] < self.HALF_ARENA and self.contains_stationary_unit(location):
                x, y = map(int, location)
                existing_unit = None
                for unit in self.game_map[x,y]:
                    if unit.stationary:
                        existing_unit = unit

                if not existing_unit.upgraded and self.config["unitInformation"][UNIT_TYPE_TO_INDEX[existing_unit.unit_type]].get("upgrade", None) is not None:
                    costs = self.type_cost(existing_unit.unit_type, True)
                    resources = self.get_resources()
                    if resources[SP] >= costs[SP] and resources[MP] >= costs[MP]:
                        self.__set_resource(SP, 0 - costs[SP])
                        self.__set_resource(MP, 0 - costs[MP])
                        existing_unit.upgrade()
                        self._build_stack.append((UPGRADE, x, y))
                        spawned_units += 1
            else:
                self.warn("Could not upgrade a unit from {}. Location has no structures or is enemy territory.".format(location))
        return spawned_units

    def get_target_edge(self, start_location):
        """Gets the target edge given a starting location

        Args:
            start_location: The location of a hypothetical unit

        Returns: 
            The edge this unit would attempt to reach if it was spawned at this location (int)
        """

        left = start_location[0] < self.HALF_ARENA
        bottom = start_location[1] < self.HALF_ARENA
        right = not(left)
        top = not(bottom)
        if left and bottom:
            return self.game_map.TOP_RIGHT
        elif left and top:
            return self.game_map.BOTTOM_RIGHT
        elif right and bottom:
            return self.game_map.TOP_LEFT
        elif right and top:
            return self.game_map.BOTTOM_LEFT

    def find_path_to_edge(self, start_location, target_edge=None):
        """Gets the path a unit at a given location would take. 
        If final point is not on an edge, it is a self destruct path

        Args:
            start_location: The location of a hypothetical unit
            target_edge: The edge the unit wants to reach. game_map.TOP_LEFT, game_map.BOTTOM_RIGHT, etc. Induced from start_location if None.

        Returns:
            A list of locations corresponding to the path the unit would take 
            to get from it's starting location to the best available end location

        """
        if self.contains_stationary_unit(start_location):
            self.warn("Attempted to perform pathing from blocked starting location {}".format(start_location))
            return

        if target_edge is None:
            target_edge = self.get_target_edge(start_location)

        end_points = self.game_map.get_edge_locations(target_edge)
        return self._shortest_path_finder.navigate_multiple_endpoints(start_location, end_points, self)

    def contains_stationary_unit(self, location):
        """Check if a location is blocked, return structures unit if it is

        Args:
            location: The location to check

        Returns:
            A structures unit if there is a stationary unit at the location, False otherwise
            
        """
        if not self.game_map.in_arena_bounds(location):
            self.warn('Checked for stationary unit outside of arena bounds')
            return False
        x, y = map(int, location)
        for unit in self.game_map[x,y]:
            if unit.stationary:
                return unit
        return False

    def warn(self, message):
        """ Used internally by game_state to print warnings
        """

        if(self.enable_warnings):
            debug_write(message)

    def suppress_warnings(self, suppress):
        """Suppress all warnings

        Args: 
            suppress: If true, disable warnings. If false, enable warnings.
            
        """

        self.enable_warnings = not suppress
        self.game_map.enable_warnings = not suppress

    def get_target(self, attacking_unit):
        """Returns target of given unit based on current map of the game board. 
        A Unit can often have many other units in range, and Units that attack do so once each frame.

        Their targeting priority is as follows:
            Infantry > Nearest Unit > Lowest Health > Lowest Y position > Closest to edge (Highest distance of X from the boards center, 13.5)

        Args:
            attacking_unit: A GameUnit

        Returns:
            The GameUnit this unit would choose to attack.

        """

        if not isinstance(attacking_unit, GameUnit):
            self.warn("Passed a {} to get_target as attacking_unit. Expected a GameUnit.".format(type(attacking_unit)))
            return

        attacker_location = [attacking_unit.x, attacking_unit.y]
        possible_locations = self.game_map.get_locations_in_range(attacker_location, attacking_unit.attackRange)
        target = None
        target_stationary = True
        target_distance = sys.maxsize
        target_health = sys.maxsize
        target_y = self.ARENA_SIZE
        target_x_distance = 0

        for location in possible_locations:
            for unit in self.game_map[location]:
                if unit.player_index == attacking_unit.player_index or (attacking_unit.damage_f == 0 and is_stationary(unit.unit_type)) or (attacking_unit.damage_i == 0 and not(is_stationary(unit.unit_type))):
                    continue

                new_target = False
                unit_stationary = unit.stationary
                unit_distance = self.game_map.distance_between_locations(location, [attacking_unit.x, attacking_unit.y])
                unit_health = unit.health
                unit_y = unit.y
                unit_x_distance = abs(self.HALF_ARENA - 0.5 - unit.x)

                if target_stationary and not unit_stationary:
                    new_target = True
                elif not target_stationary and unit_stationary:
                    continue
                
                if target_distance > unit_distance:
                    new_target = True
                elif target_distance < unit_distance and not new_target:
                    continue

                if target_health > unit_health:
                    new_target = True
                elif target_health < unit_health and not new_target:
                    continue

                # Compare height heuristic relative to attacking unit's player index
                if attacking_unit.player_index == 0:
                    if target_y > unit_y:
                        new_target = True
                    elif target_y < unit_y and not new_target:
                        continue
                else:
                    if target_y < unit_y:
                        new_target = True
                    elif target_y > unit_y and not new_target:
                        continue

                if target_x_distance < unit_x_distance:
                    new_target = True
                
                if new_target:
                    target = unit
                    target_stationary = unit_stationary
                    target_distance = unit_distance
                    target_health = unit_health
                    target_y = unit_y
                    target_x_distance = unit_x_distance
        return target

    def get_attackers(self, location, player_index):
        """Gets the stationary units threatening a given location

        Args:
            location: The location of a hypothetical defender
            player_index: The index corresponding to the defending player, 0 for you 1 for the enemy

        Returns:
            A list of units that would attack a unit controlled by the given player at the given location

        """

        if not player_index == 0 and not player_index == 1:
            self._invalid_player_index(player_index)
        if not self.game_map.in_arena_bounds(location):
            self.warn("Location {} is not in the arena bounds.".format(location))

        attackers = []
        """
        Get locations in the range of TURRET units
        """
        max_range = 0
        for unit in self.config["unitInformation"]:
            if unit.get('attackRange', 0) >= max_range:
                max_range = unit.get('attackRange', 0)
        possible_locations= self.game_map.get_locations_in_range(location, max_range)
        for location_unit in possible_locations:
            for unit in self.game_map[location_unit]:
                if unit.damage_i + unit.damage_f > 0 and unit.player_index != player_index and self.game_map.distance_between_locations(location, location_unit) <= unit.attackRange:
                    attackers.append(unit)
        return attackers
