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

        self.execute_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def execute_strategy(self, game_state):
        """
        Execute the strategy

        Building defenses and creating mobile units on offense.
        """

        self.build_defences(game_state)
        self.spawn_attackers(game_state)
        #  self.remove_defenses(game_state)


    def build_defences(self, game_state):
        """
        Build defenses
        """
        turn_number = game_state.turn_number

        if turn_number == 0:
            turret_locations = [[3, 12], [24, 12], [10, 10], [17, 10]]
            game_state.attempt_spawn(TURRET, turret_locations)
            game_state.attempt_upgrade(turret_locations)

            wall_locations = [[2, 12], [2, 13], [4, 12], [23, 12], [24, 13], [25, 12]]
            game_state.attempt_spawn(WALL, wall_locations)

            game_state.attempt_remove(wall_locations)
        elif turn_number == 1:
            wall_locations = [[1, 13], [2, 12], [3, 13], [24, 13], [25, 12], [26, 13]]
            game_state.attempt_spawn(WALL, wall_locations)

            support_locations = [[17, 6]]
            game_state.attempt_spawn(SUPPORT, support_locations)

            game_state.attempt_remove(wall_locations + support_locations)
        elif turn_number == 2:
            wall_locations_1 = [[4, 11], [5, 10], [6, 9], [7, 8], [8, 7], [9, 6], [10, 5], [11, 4], [12, 3], [13, 2], [14, 2]]
            game_state.attempt_spawn(WALL, wall_locations_1)

            wall_locations_2 = [[15, 3], [16, 4], [17, 5], [18, 6], [19, 7], [20, 8]]
            game_state.attempt_spawn(WALL, wall_locations_2)

            wall_locations_3 = [[0, 13], [1, 13], [2, 13], [26, 13], [27, 13]]
            game_state.attempt_spawn(WALL, wall_locations_3)

            game_state.attempt_remove(wall_locations_3 + [[10,10],[17,10]])
        elif turn_number == 3:
            wall_locations_1 = [[0, 13], [1, 13], [2, 13], [4, 13], [24, 13], [25, 13], [26, 13], [27, 13]]
            game_state.attempt_spawn(WALL, wall_locations_1)

            wall_locations_2 = [[4, 12], [21, 12], [22, 12][23, 12], [19, 9], [19, 10], [20, 10]]
            game_state.attempt_spawn(WALL, wall_locations_2)

            turret_locations = [[20, 9], [22, 11]]
            game_state.attempt_spawn(TURRET, turret_locations)

            game_state.attempt_remove(wall_locations_1 + wall_locations_2 + turret_locations)
        elif turn_number == 4:
            turret_locations = [[20, 9], [22, 11]]
            game_state.attempt_spawn(TURRET, turret_locations)
            game_state.attempt_upgrade([[20, 9]])

            wall_locations = [[0, 13], [1, 13], [2, 13], [4, 13], [24, 13], [25, 13], [26, 13], [27, 13], [4, 12], [23, 12]]
            game_state.attempt_spawn(WALL, wall_locations)

            game_state.attempt_remove(wall_locations)
        elif turn_number >= 5:
            pass


    def spawn_attackers(self, game_state):
        """
        Prepare attackers for action phase
        """
        turn_number = game_state.turn_number

        if turn_number == 0:
            pass
        elif turn_number == 1:
            scount_locations = [[20, 6]]
            scount_count = 7
            game_state.attempt_spawn(SCOUT, scount_locations, scount_count)
        elif turn_number == 2:
            interceptor_locations = [[20, 6]]
            interceptor_count = 1
            game_state.attempt_spawn(INTERCEPTOR, interceptor_locations, interceptor_count)
        elif turn_number == 3:
            interceptor_locations = [[22,8],[23,9]]
            interceptor_count = 2
            game_state.attempt_spawn(INTERCEPTOR, interceptor_locations, interceptor_count)
        elif turn_number == 4:
            interceptor_locations = [[22,8]]
            interceptor_count = 2
            game_state.attempt_spawn(INTERCEPTOR, interceptor_locations, interceptor_count)
        elif turn_number >= 5:
            pass


    #  def remove_defenses(self, game_state):
    #      """
    #      Plan removal of defensive buildings after action phase
    #      """
    #      pass

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
