import json

from .game_state import GameState
from .util import get_command, debug_write, BANNER_TEXT, send_command

class AlgoCore(object):
    """This class handles communication with the game itself. Your strategy should subclass it.

    Attributes:
        * config (JSON): json object containing information about the game

    """
    def __init__(self):
        self.config = None

    def on_game_start(self, config):
        """
        Override this to perform initial setup at the start of the game, based
        on the config, a json file which contains information about the game.
        """
        self.config = config

    def on_turn(self, game_state):
        """
        This step function is called every turn and is passed a string containing
        the current game state, which can be used to initialize a new GameMap
        """
        self.submit_default_turn()

    def submit_default_turn(self):
        send_command("")
        send_command("")

    # only override this function if you have a 
    def start(self):
        """ 
        Start the parsing loop.
        Python will hang on the readline() statement so actually this program will run forever unless manually stopped or
        it receives the "End" turn message from the game.
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
                    If stateType == 1, this game_state_string string represents the results of an action phase
                    """
                    continue
                elif stateType == 2:
                    """
                    This is the end game message. This means the game is over so break and finish the program.
                    """
                    debug_write("Got end state quitting bot.")
                    break
                else:
                    """
                    Something is wrong? Recieved an incorrect or imporperly formatted string.
                    """
                    debug_write("Got unexpected string with turnInfo: {}".format(game_state_string))
            else:
                """
                Something is wrong? Recieved an incorrect or imporperly formatted string.
                """
                debug_write("Got unexpected string : {}".format(game_state_string))
