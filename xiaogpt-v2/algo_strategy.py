import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))
        # defensive_stage is for when i should add more turrets
        self.defensive_stage = 0
        self.first_support = [[2, 12], [1, 12]]
        self.second_support = [[2, 11], [3, 11]]
        self.third_support = [[8,8],[9,8],[9,7],[10,7]]
        self.second_wall = [[6, 13], [22, 13], [23, 13], [24, 13], [25, 13], [26, 13]]
        
        
        self.interceptor_destruct_strategy_wall = [[17, 9], [18, 9], [19, 9], [20, 9], [21, 9], [22, 9], [23, 9], [17, 8], [17, 7], [18, 7], [19, 7], [20, 7], [21, 7]]
        self.interceptor_str_deploy = [[22, 8]]
        #! notice I hard code this wall that will never be destroyed, to indecate the self destruct strategy
        self.wall_indecate_self_destruct_strategy = [[17,4]]
        self.attack_from_left = False
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

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

# Key takeaway: if you want a wall to be defensive, upgrade it
# 
# Steps:
# 1. Set up the V wall
# 2. Set up the five horizontal wall on the left
# 3. The space below the five horizontal wall 
    def get_MP(self, game_state, player):
        return game_state.get_resource(1, player)
    def get_SP(self, game_state, player):
        return game_state.get_resource(0, player)

    # helper function, given a list of location return number of units

    # explode
    # right weak, right have attack
    def number_of_units_on_the_locations(self,game_state,locations):
        # get count of units on the locations
        count = 0
        for loc in locations:
            count = count +1 if game_state.contains_stationary_unit(loc) else count
        return count
        
    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        self.fix_health(game_state)
        # STAGE 1: Build defensive wall
        self.build_stage1_defences(game_state)
        # STAGE 2: Build additional wall
        self.build_stage2_defence(game_state)
        # STAGE 3: Build essential first support
        self.build_stage3_defence(game_state)
        self.integrate_defensive_turrets(game_state)
        self.build_third_supports(game_state)
        self.trigger_attack(game_state)
        if(self.get_MP(game_state, 0) >= 18):
            self.launch_attack_full(game_state)
        


    def build_second_wall(self,game_state):
        game_state.attempt_spawn(WALL, self.second_wall)
        
    def fix_health(self, game_state):
        # recycle bad walls and stuff
        for y in range(13):
            for x in range(13-y, 15+y):
                for unit in game_state.game_map[x,y]:
                    if unit.stationary:
                        if unit.health < unit.max_health * 0.25:
                            game_state.attempt_remove([x,y])
        
    def integrate_defensive_turrets(self, game_state):
        # upgrade defensive turrets
        count_of_all_support = self.number_of_units_on_the_locations(game_state, self.first_support + self.second_support + self.third_support)
        my_SP = self.get_SP(game_state, 0)
        if count_of_all_support >= 4 and my_SP > 4 and self.defensive_stage == 0:
            self.defensive_stage = 1
            # recycle the previous walls and stuff to build stronger turrets
            game_state.attempt_remove([[7,9], [8, 9]])
    
        
    def build_stage1_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[4, 12], [7, 9]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(TURRET, turret_locations)
        # Place walls in front of turrets to soak up damage for them
        wall_locations = [[0, 13], [1, 13], [2, 13], [3,13], [4,13], [5,13], [27, 13], [26, 12], [25, 11], [24, 10], [23, 9], [21, 7], [20, 6], [19, 5], [18, 4], [17, 3], [16, 3],[15,3],[14,3],[13,3],[12,3],[11,4],[10,5],[9,6],[8,7],[7,8],[6,9],[7,10]]
        
        
        upgraded_wall_locations = [[0, 13], [1, 13], [2, 13], [3,13], [4,13], [5,13],[8,7],[6,9],[7,10]]
        
        game_state.attempt_spawn(WALL, wall_locations)

        # we are not in destruct defense strategy
        if not self.if_indicator_destruct_str(game_state):
            game_state.attempt_spawn(WALL, self.interceptor_str_deploy)

        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(upgraded_wall_locations)


    def if_indicator_destruct_str(self, game_state):
        return game_state.contains_stationary_unit(self.wall_indecate_self_destruct_strategy[0])
        

    def build_stage2_defence(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[5, 12]]if self.defensive_stage == 0 else [[5, 12], [3, 12], [8,9]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(TURRET, turret_locations)
        
        # Place walls in front of turrets to soak up damage for them
        wall_location1 = [[6, 12]]
        game_state.attempt_spawn(WALL, wall_location1)
        game_state.attempt_upgrade(wall_location1)
        wall_location2 = [[8,9]] if self.defensive_stage == 0 else [[8,10],[9,9]]
        wall_location2 += [[27,13], [26, 12], [25, 11]]
        game_state.attempt_spawn(WALL, wall_location2)
        game_state.attempt_upgrade(wall_location2)
        # if(game_state.turn_number % 4 == 0):
        #     self.build_second_wall(game_state)
        

    def build_stage3_defence(self, game_state):
        opponent_MP = self.get_MP(game_state, 1)
        
        if opponent_MP > 12:
            self.upgrade_turrets(game_state)
            self.build_first_supports(game_state)  
        else:
            self.build_first_supports(game_state)  
            self.upgrade_turrets(game_state)

        # we check if we are / plan to use strategy of self-destruct interceptor
        
        if self.if_indicator_destruct_str(game_state) or len(self.scored_on_locations) > 0:
            
            self.deploy_self_drstruct_strategy(game_state)
        
        

        count_of_first_support = self.number_of_units_on_the_locations(game_state, self.first_support)
        if(count_of_first_support == 2):
            # only build second supports if first are all built
            
            self.build_second_supports(game_state)
    
    
    def deploy_self_drstruct_strategy(self, game_state):
        game_state.attempt_spawn(WALL, self.interceptor_destruct_strategy_wall + self.wall_indecate_self_destruct_strategy)
        game_state.attempt_remove(self.interceptor_str_deploy)
        game_state.attempt_spawn(INTERCEPTOR, self.interceptor_str_deploy)
        
    
        
    def build_third_supports(self, game_state):
        game_state.attempt_spawn(SUPPORT, self.third_support)
        game_state.attempt_upgrade(self.third_support)

    def trigger_attack(self, game_state):
        """
        Trigger an attack if we have enough resources.
        """
        count_of_all_support = self.number_of_units_on_the_locations(game_state, self.first_support + self.second_support)
        my_MP = self.get_MP(game_state, 0)
        # if we have enough money, launch an attack
            # if there is lots of supports, launch a strong attack
        if(count_of_all_support >= 2 and count_of_all_support <= 4):
            if(my_MP >= 12):
                self.launch_attack_weak(game_state)
        elif(count_of_all_support > 4):            
            if(my_MP >= 10):
                self.launch_attack_weak(game_state)

    def build_second_supports(self, game_state):
        
        game_state.attempt_spawn(WALL, [4,11])
        game_state.attempt_upgrade([4,11])
        
        for location in self.second_support:
            if self.get_SP(game_state, 0) <= 5:
                # if we have money less /equal than 5, save it for future defense
                break
            game_state.attempt_spawn(SUPPORT, location)
            game_state.attempt_upgrade(location)
        

    def build_first_supports(self, game_state):
        """
        Build basic supports using hardcoded locations.
        """

        # Place walls in front of turrets to soak up damage for them
        support_locations = self.first_support
        game_state.attempt_spawn(SUPPORT, support_locations)
        game_state.attempt_upgrade(support_locations)
    def build_third_supports(self, game_state):
        game_state.attempt_spawn(SUPPORT, self.third_support)
        game_state.attempt_upgrade(self.third_support)
    def launch_attack_weak(self, game_state):
        spawn_location = [12, 1] if self.attack_from_left else [15, 1] 
        game_state.attempt_spawn(DEMOLISHER, spawn_location, 2)
        game_state.attempt_spawn(SCOUT, spawn_location, 1000)
    
    def launch_attack_strong(self, game_state):
        game_state.attempt_spawn(SCOUT, [15,1], 1000)
    def launch_attack_full(self, game_state):
        game_state.attempt_spawn(DEMOLISHER, [15, 1] , 1000)
    def upgrade_turrets(self, game_state):
        turret_locations = [[5, 12], [7, 9], [4, 12]] if self.defensive_stage == 0 else [[5, 12], [7, 9], [4, 12], [3, 12], [8,9]]
        game_state.attempt_upgrade(turret_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # Remove locations that are blocked by our own structures 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
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

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
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
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
