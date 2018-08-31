import json

from .game import GameMap
from .util import get_command, debug_write, BANNER_TEXT


"""
NOTICE: You should not need to modify this file to implement your algo's
strategy, if you are wondering where to start please look at algo_strategy.py
"""

class AlgoCore(object):
    def __init__(self):
        self.config = None

    def process_config(self, config):
        """
        Tweak your strategy based on the parsed config and perform any initial
        algo setup. This function will be allowed to run for a short time, the
        exact duration is undetermined but will likely be a single digit number
        of seconds.

        This default implementation performs no additional processing based on
        the received config
        """
        self.config = config

    def step(self, game_map):
        """
        This step function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the board and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.

        This default implementation spawns no units before ending its turn
        """
        game_map.send_messages()

    # only override this function if you feel confident in your debugging abilities
    def start(self):
        """ start the parsing loop
        Python will hang on the readline() statement so actually this program will run forever unless manually stopped or
        it receives the "End" turn message from the game.
        """
        debug_write(BANNER_TEXT)

        while True:
            # Note: Python blocks and hangs on stdin. Can cause issues if connections aren't setup properly and may need to
            # manually kill this Python program.
            cmd = get_command()
            if "startingFood" in cmd:
                '''
                This means this must be the config file. So, load in the config file as a json and add it to your AiLogic class.
                '''
                parsed_config = json.loads(cmd)
                self.process_config(parsed_config)
            elif "turnInfo" in cmd:
                state = json.loads(cmd)
                stateType = int(state.get("turnInfo")[0])
                if stateType == 0:
                    '''
                    This is the game turn game state message. Algo must now print to stdout 2 lines, one for build phase one for
                    deploy phase.
                    '''
                    game_map = GameMap(self.config, cmd)
                    self.step(game_map)
                elif stateType == 1:
                    '''
                    Currently this ignores action phase states but other algos might find it useful to look at them. 
                    For example to analyze and predict Deployment patterns in the enemy, or to get quick heuristics like
                    how much shields does the enemy get by looking at HP of soldiers.
                    '''
                    continue
                elif stateType == 2:
                    '''
                    This is the end game message. This means the game is over so break and finish the program.
                    '''
                    debug_write("Got end state quitting bot.")
                    break
                else:
                    '''
                    Something is wrong? Shouldn't ever get here unless you are running this algo separate from a game 
                    and are sending weird unformatted messages.
                    '''
                    debug_write("Got unexpected string with turnInfo: {}".format(cmd))
            else:
                '''
                Something is wrong? Shouldn't ever get here unless you are running this algo separate from a game 
                and are sending weird unformatted messages.
                '''
                debug_write("Got unexpected string : {}".format(cmd))
