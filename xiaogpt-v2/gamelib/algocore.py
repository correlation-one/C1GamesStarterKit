import json

from .game_state import GameState
from .util import get_command, debug_write, BANNER_TEXT, send_command

class AlgoCore(object):
    """
    This class handles communication with the game engine. \n
    algo_strategy.py subclasses it. 

    Attributes :
        * config (JSON): json object containing information about the game

    """
    def __init__(self):
        self.config = None

    def on_game_start(self, config):
        """
        This function is called once at the start of the game. 
        By default, it just initializes the config. \n
        You can override it it in algo_strategy.py to perform start of game setup
        """
        self.config = config

    def on_turn(self, game_state):
        """
        This step function is called at the start of each turn.
        It is passed the current game state, which can be used to initiate a new GameState object. 
        By default, it sends empty commands to the game engine. \n
        algo_strategy.py inherits from AlgoCore and overrides this on turn function. 
        Adjusting the on_turn function in algo_strategy is the main way to adjust your algo's logic. 
        """
        send_command("[]")
        send_command("[]")
    
    def on_action_frame(self, action_frame_game_state):
        """
        After each deploy phase, the game engine will run the action phase of the round.
        The action phase is made up of a sequence of distinct frames. 
        Each of these frames is sent to the algo in order. 
        They can be handled in this function. 
        """
        pass


    def start(self):
        """ 
        Start the parsing loop.
        After starting the algo, it will wait until it recieves information from the game 
        engine, proccess this information, and respond if needed to take it's turn. 
        The algo continues this loop until it recieves the "End" turn message from the game.
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
