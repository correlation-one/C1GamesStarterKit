import gamelib
import random
import math
import warnings
from sys import maxsize
import json
import os
import torch

from gamelib.util import get_command, debug_write, BANNER_TEXT, send_command

from ppo import PPO


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

        self.modelconfig = [
            28*28 + 7, 
            14*28, 
            3e-4, 
            1e-3, 
            0.99, 
            40, 
            0.2, 
            True
        ]

        self.rewards = {
            'invalid_placement': -0.1,
            'health': {
                'a': 2,
                'def': -0.5
            },
            'mp': {
                'a': 0.5,
                'def': -0.1
            },
            'sp': {
                'a': 0.5,
                'def': -0.1
            }
        }

        self.model = PPO(*self.modelconfig)
        self.model_num = 0

        self.action_std_decay_rate = 0
        self.min_action_std = 0
        self.action_std_decay_freq = 0

        self.prev_reward_calc = {
            'health': -1,
            'ehealh': -1,
            'mp': -1,
            'sp': -1,
            'invp': 0
        }

        self.equivsp = 0

        directory = "PPO_preTrained/terminal"
        if os.path.exists(directory) and os.listdir(directory):
            load_path = max([f for f in os.scandir(directory)], key=lambda x: x.stat().st_mtime).name
            load_dir = directory + '/terminal/' + load_path
            self.model.load(load_dir)
            self.model_num = len(os.listdir(directory))

        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, UNIT_TYPE_TO_INDEX
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

    def start(self):
        """ 
        Start the parsing loop.
        After starting the algo, it will wait until it receives information from the game 
        engine, process this information, and respond if needed to take it's turn. 
        The algo continues this loop until it receives the "End" turn message from the game.
        """
        debug_write(BANNER_TEXT)

        while True:
            # Note: Python blocks and hangs on stdin. Can cause issues if connections aren't setup properly and may need to
            # manually kill this Python program.
            game_state_string = get_command()
            if "replaySave" in game_state_string:
                """
                This means this must be the config file. So, load in the config file as a json and add it to your AlgoStrategy class.
                """
                parsed_config = json.loads(game_state_string)
                self.on_game_start(parsed_config)
            elif "turnInfo" in game_state_string:
                state = json.loads(game_state_string)
                stateType = int(state.get("turnInfo")[0])
                if stateType == 0:
                    """
                    This is the game turn game state message. Algo must now print to stdout 2 lines, one for build phase one for
                    deploy phase. Printing is handled by the provided functions.
                    """
                    self.on_turn(game_state_string)
                elif stateType == 1:
                    """
                    If stateType == 1, this game_state_string string represents a single frame of an action phase
                    """
                    self.on_action_frame(game_state_string)
                elif stateType == 2:
                    """
                    This is the end game message. This means the game is over so break and finish the program.
                    """
                    game_state = gamelib.GameState(self.config, game_state_string)
                    self.model.buffer.rewards.append(self.reward(game_state))
                    self.model.buffer.is_terminals.append(True)

                    directory = "PPO_rewards/"
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    directory = directory + '/terminal/'
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    checkpoint_path = directory + "PPO_{}.json".format(self.model_num)
                    with open(checkpoint_path, 'w') as f:
                        json.dumps(self.model.buffer.json(), f)

                    debug_write("Got end state, game over. Stopping algo.")
                    break
                else:
                    """
                    Something is wrong? Received an incorrect or improperly formatted string.
                    """
                    debug_write("Got unexpected string with turnInfo: {}".format(game_state_string))
            else:
                """
                Something is wrong? Received an incorrect or improperly formatted string.
                """
                debug_write("Got unexpected string : {}".format(game_state_string))

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        mapped = [[0 for i in range(28)] for i in range(28)]
        self.equivsp = 0

        for i in range(28):
            for j in range(28):
                if game_state.game_map.in_arena_bounds([i, j]):
                    arr = game_state.game_map.__getitem__([i, j])
                    if len(arr) > 0:
                        mapped[i][j] = UNIT_TYPE_TO_INDEX[arr[0].unit_type] + 1
                        if j <= 13:
                            self.equivsp += 0.75 * (arr[0].cost[0]) * (arr[0].health / arr[0].max_health)

        inp = torch.cat(torch.reshape(torch.tensor(mapped), (28*28,)), torch.tensor([
            game_state.get_resource('MP', 0),
            game_state.get_resource('SP', 0),
            game_state.my_health,
            game_state.get_resource('MP', 1),
            game_state.get_resource('SP', 1),
            game_state.enemy_health,
            game_state.turn_number
        ]), 0)

        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        if game_state.turn_number > 0:
            self.model.buffer.rewards.append(self.reward(game_state))
            self.model.buffer.is_terminals.append(False)
        
        self.prev_reward_calc = {
            'health': game_state.my_health,
            'ehealth': game_state.enemy_health,
            'mp': game_state.get_resource('MP', 0),
            'sp': game_state.get_resource('SP', 0),
            'board_equiv_sp': self.equivsp,
            'invp': 0
        }

        action = self.model.select_action(inp, (28, 14))
        self.action_to_strat(action)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def reward(self, game_state):
        return (
            (game_state.health - self.prev_reward_calc['health'])*self.dim(self.prev_reward_calc['health'], self.rewards['health']['a'])*self.rewards['health']['def'] +
            (self.prev_reward_calc['ehealth'] - game_state.enemy_health)*self.dim(self.prev_reward_calc['ehealth'], self.rewards['health']['a'])*self.rewards['health']['def'] +
            (game_state.get_resource('MP', 0) - self.prev_reward_calc['mp'])*self.dim(self.prev_reward_calc['mp'], self.rewards['mp']['a'])*self.rewards['mp']['def'] + 
            (game_state.get_resource('SP', 0) + self.prev_reward_calc['board_equiv_sp'] - self.equivsp - self.prev_reward_calc['sp'])*self.dim(self.prev_reward_calc['sp'], self.rewards['sp']['a'])*self.rewards['sp']['def'] +
            self.prev_reward_calc['invp']
        )

    def action_to_strat(self, action, game_state):
        reference = [WALL, TURRET, SUPPORT, WALL, TURRET, SUPPORT, SCOUT, DEMOLISHER, INTERCEPTOR]
        for i in range(28):
            for j in range(14):
                if action[i][j] != 0:
                    if game_state.game_map.in_arena_bounds((i, j)):
                        if action[i][j] == 10:
                            if not game_state.contains_stationary_unit((i, j)):
                                self.prev_reward_calc['invp'] += self.rewards['invalid_placement']
                            else:
                                game_state.attempt_remove([i, j])
                        elif not game_state.contains_stationary_unit((i, j)):
                            if action[i][j] <= 6 and action[i][j] >= 4:
                                if game_state.get_resources()[0] >= game_state.type_cost(reference[action[i][j] - 1], True)[0] + game_state.type_cost(reference[action[i][j] - 1])[0]:
                                    game_state.attempt_spawn(reference[action[i][j] - 1], [(i, j)], 1)
                                    game_state.attempt_upgrade([(i, j)])
                                else:
                                    self.prev_reward_calc['invp'] += self.rewards['invalid_placement']
                            else:
                                if game_state.can_spawn(reference[action[i][j] - 1], (1, j), 1):
                                    game_state.attempt_spawn(reference[action[i][j] - 1], [(i ,j)], 1)
                                else:
                                    self.prev_reward_calc['invp'] += self.rewards['invalid_placement']
                        else:
                            self.prev_reward_calc['invp'] += self.rewards['invalid_placement']
                    else:
                        self.prev_reward_calc['invp'] += self.rewards['invalid_placement']

    def dim(self, prev, a):
        return a * 2**(-prev/5) + 1

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
