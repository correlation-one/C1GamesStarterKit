import gamelib
import random
import math
from sys import maxsize


"""
You are able to implement your own algo by subclassing the `AlgoCore` class and
overriding the methods `process_config(config_string)` and `step(game_map)`.
Most of the algo code you write will be in this file unless you create new
modules yourself.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def process_config(self, config):
        """ Tweak strategy based on config and perform any initial algo setup """
        gamelib.debug_write('Configuring your custom algo strategy...')

        self.config = config
        self.tank = "SI"
        self.sniper = "EI"
        self.fast = "PI"
        self.wall = "FF"
        self.shooting = "DF"
        self.shield = "EF"

    def step(self, game_map):
        """
        This step function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_map.turn_number))

        self.starter_strategy(game_map)  # replace with your own strategy

        game_map.send_messages()

    # NOTE: All the methods after this point are part of the sample starter strategy. 
    def starter_strategy(self, game_map):
        first_turn = game_map.turn_number == 0
        if first_turn:
            self.turn_one_defences(game_map)
        else:
            self.build_defences(game_map)
            self.deploy_attackers(game_map)

    #On turn one, we make the C1 Logo!
    def turn_one_defences(self, game_map):
        #Make our letter C
        firewall_locations = [[8, 11], [9, 11], [7,10], [7, 9], [7, 8], [8, 7], [9, 7]]
        game_map.attempt_spawn_multiple(self.wall, firewall_locations)
        
        #Make our number 1
        firewall_locations = [[17, 11], [18, 11], [18, 10], [18, 9], [18, 8], [17, 7], [18, 7], [19,7]]
        game_map.attempt_spawn_multiple(self.wall, firewall_locations)

        #Build our 3 dots
        firewall_locations = [[11, 7], [13, 9], [15, 11]]
        game_map.attempt_spawn_multiple(self.shooting, firewall_locations)

    def build_defences(self, game_map):
        #Choose to spend a random amount of cores
        starting_cores = game_map.get_resource('cores')
        cores_to_spend = random.randint(0, math.floor(starting_cores))

        #Get all locations on the bottom half of the map
        all_locations = [[0, 0]]
        for i in range(game_map.arena_size):
            for j in range(math.floor(game_map.arena_size / 2)):
                all_locations.append([i, j])
        possible_locations = game_map.filter_blocked_locations(all_locations)

        #While we still want to spend more cores, build a random firewall
        while cores_to_spend >= game_map.type_cost(self.wall) and len(possible_locations) > 0:
            location_index = random.randint(0, len(possible_locations) - 1)
            build_location = possible_locations[location_index]
            possible_locations.remove(build_location)

            firewall_number = random.randint(1, 3)
            if firewall_number == 1 or cores_to_spend < 6:
                cores_to_spend -= game_map.type_cost(self.wall)
                firewall_to_build = self.wall
            elif firewall_number == 2 or cores_to_spend < 8:
                cores_to_spend -= game_map.type_cost(self.shooting)
                firewall_to_build = self.shooting
            else:
                cores_to_spend -= game_map.type_cost(self.shield)
                firewall_to_build = self.shield

            game_map.attempt_spawn(firewall_to_build, build_location)

    def deploy_attackers(self, game_map):
        #Get some variebles we will use
        starting_bits = game_map.get_resource('bits')
        bits_to_spend = random.randint(0, math.floor(starting_bits))
        enemy_bits = game_map.get_resource('bits', 1)
        current_health = game_map.my_integrity
        enemy_health = game_map.enemy_integrity
        friendly_edges = game_map.get_edge_locations("bottom_left") + game_map.get_edge_locations("bottom_right")
        deploy_locations = game_map.filter_blocked_locations(friendly_edges)

        #While we still want to spend more bits, deploy a random information unit
        while bits_to_spend >= game_map.type_cost(self.fast) and len(deploy_locations) > 0:
            ping_value = 1
            scrambler_value = 1
            emp_value = 1

            #Stop if values were set below zero
            if ping_value + scrambler_value + emp_value < 1:
                break

            #Choose a random deploy location
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            #Adjust weights slightly based on game state
            if enemy_health <= 5:
                ping_value *= 2

            if enemy_bits > starting_bits or current_health <= 5:
                scrambler_value *= 2
            if bits_to_spend < 3:
                emp_value = 0

            #Choose a random unit based on weights, higher weights are more likely to be chosen
            total_value = ping_value + scrambler_value + emp_value
            choice = random.randint(1, total_value)

            if choice <= ping_value:
                bits_to_spend -= game_map.type_cost(self.fast)
                unit_to_spawn = self.fast
            elif choice <= ping_value + scrambler_value:
                bits_to_spend -= game_map.type_cost(self.tank)
                unit_to_spawn = self.tank
            else:
                bits_to_spend -= game_map.type_cost(self.sniper)
                unit_to_spawn = self.sniper

            game_map.attempt_spawn(unit_to_spawn, deploy_location)

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
