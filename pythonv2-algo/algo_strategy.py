import gamelib
import random
import math
import warnings
from sys import maxsize
import json
from itertools import repeat, product
from copy import deepcopy


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""
corner_wall_points = [[0, 13], [1, 13], [2, 13], [3, 13], [
    24, 13], [25, 13], [26, 13], [27, 13], [2, 12], [25, 12]]
outer_wall_points = [[4, 13], [5, 13], [6, 13], [7, 13], [11, 13], [12, 13], [
    13, 13], [14, 13], [15, 13], [16, 13], [20, 13], [21, 13], [22, 13], [23, 13]]
suicide_pocket_points = [[8, 13], [10, 13],
                         [9, 12], [17, 13], [19, 13], [18, 12]]
turret_points = [[3, 12], [4, 12], [7, 12], [11, 12], [16, 12], [20, 12], [
    23, 12], [24, 12], [7, 9], [11, 9], [16, 9], [20, 9], [22, 9]]
interceptor_points = [[4, 9], [5, 8], [22, 8], [20, 6]]
inner_wall_points = [[1, 12], [26, 12], [2, 11], [25, 11], [3, 10], [4, 10], [5, 10], [6, 10], [7, 10], [11, 10], [12, 10], [13, 10], [
    14, 10], [15, 10], [16, 10], [20, 10], [21, 10], [22, 10], [23, 10], [24, 10], [8, 9], [10, 9], [17, 9], [19, 9], [9, 8], [18, 8]]
support_points = [[12, 6], [13, 6], [15, 6], [16, 6], [12, 5], [13, 5], [15, 5], [16, 5], [12, 4], [13, 4], [15, 4], [
    16, 4], [12, 3], [13, 3], [15, 3], [16, 3], [12, 2], [13, 2], [15, 2], [16, 2], [12, 1], [13, 1], [15, 1], [13, 0]]
cannon_launch_points = [[14, 0]]


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.meridian_breaches = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write(
            'Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        # Comment or remove this line to enable warnings.
        game_state.suppress_warnings(True)

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)
        # First, place basic defenses
        self.build_defences(game_state)

        # If the turn is less than 5, stall with interceptors and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_interceptors(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our demolishers to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.demolisher_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Scouts there.

                # Only spawn Scouts every other turn
                # Sending more at once is better since attacks can only hit a single scout at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    scout_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(
                        game_state, scout_spawn_location_options)
                    game_state.attempt_spawn(SCOUT, best_location, 1000)

                # Lastly, if we have spare SP, let's build some Factories to generate more resources
                support_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(SUPPORT, support_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        game_state.attempt_spawn(WALL, corner_wall_points)
        game_state.attempt_spawn(WALL, outer_wall_points)
        game_state.attempt_spawn(WALL, suicide_pocket_points)
        game_state.attempt_spawn(TURRET, turret_points)
        game_state.attempt_spawn(
            INTERCEPTOR, interceptor_points)  # todo only some
        game_state.attempt_spawn(WALL, inner_wall_points)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """
        game_state.attempt_upgrade(corner_wall_points)
        game_state.attempt_upgrade(suicide_pocket_points)
        game_state.attempt_upgrade(turret_points)
        for location in self.meridian_breaches:
            build_location = [location, 12]
            game_state.attempt_spawn(WALL, build_location)
        self.meridian_breaches = []
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own structures
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(
            friendly_edges, game_state)

        # While we have remaining MP to spend lets send out interceptors randomly.
        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(INTERCEPTOR, deploy_location)
            """
            We don't have to remove the location since multiple mobile
            units can occupy the same space.
            """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, SUPPORT]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def enemy_damage_heatmap(self, game_state, locations=None):
        '''Finds the weakest point in an enemy defense
        Tries to find the weakest point based on turret density
        Doesn't use the refund policy - assumes a constant map from the previous
        round. Will probably be effective in early rounds, but not in later
        round. This is effectively `least_damage_spawn_location`'''
        # iterate over enemy map
        heatmap = []
        # Use generators because we like space
        if not locations:
            locations = zip(range(game_state.ARENA_SIZE), [*range(game_state.HALF_ARENA, game_state.ARENA_SIZE),
                                                           *range(game_state.ARENA_SIZE - 1, game_state.HALF_ARENA - 1, -1)])
        for location in locations:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                for attacker in game_state.get_attackers(path_location, 0):
                    damage += attacker.damage_i
            heatmap.append(damage)
        return heatmap

    def demolisher_sim(self, game_state):
        # from each starting point, spawn **SOME NUMBER OF** demolishers (if possible)
        # test if the demolisher can punch a hole into the enemy wall
        heatmap = []
        DEM = gamelib.GameUnit(DEMOLISHER, game_state.config)
        # test all spawn locations - if this is too slow, we'll reduce the search space
        for starting_position in zip(range(game_state.game_map.HALF_ARENA), range(game_state.game_map.HALF_ARENA, -1, -1)):
            current_position = list(starting_position)

            # CHECK IF WE'LL REMOVE A WALL ON AN EDGE THAT COULD CHANGE WHETHER
            # WE CAN SPAWN FROM THIS `starting position`
            if not game_state.can_spawn(current_position):
                continue

            # create a deepcopy to manipulate the map for each simulation
            statecopy = deepcopy(game_state)
            start_location_stats = []
            while True:
                path = statecopy.find_path_to_edge(current_position)
                dem_health = DEM.health
                current_position = path[1]
                if dem_health <= 0:
                    break
                target = statecopy.get_target(DEM, current_position)

                dem_health -= len(statecopy.get_attackers(current_position, 0)
                                  ) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            start_location_stats.append(dmg)

    def least_damage_spawn_location(self, game_state, location_options=None):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        # Get the damage estimate each path will take
        heatmap = self.enemy_density_heatmap(game_state, location_options)
        # Now just return the location that takes the least damage
        if location_options:
            return location_options[damages.index(min(damages))]
        else:
            index = damages.index(min(damages))
            if index < game_state.HALF_ARENA:
                return [index, game_state.HALF_ARENA + index]
            else:
                return [index, game_state.ARENA_SIZE - (index - game_state.HALF_ARENA) - 1]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        moves = events["move"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write(
                    "All locations: {}".format(self.scored_on_locations))
        for move in moves:
            prev_location = move[0]
            after_location = move[1]
            if prev_location[1] == 14 and after_location[1] == 13:
                self.meridian_breaches.append(after_location[0])


if __name__ == "__main__":
    # algo = AlgoStrategy()
    # algo.start()
    bigmac = 28
    halfmac = 14
    # pos = ([x, y] for y in range(halfmac, bigmac)
    #        for x in range(y - halfmac, bigmac - (y - halfmac)))
    # pos = zip(range(bigmac), [*range(halfmac, bigmac),
    #                           *range(bigmac - 1, halfmac - 1, -1)])
