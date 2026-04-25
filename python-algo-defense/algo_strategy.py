import gamelib
import random
import os
import json
from sys import maxsize

from strategies import STRATEGIES


"""
algo_strategy.py — Entry point for the Terminal algo.

Set the STRATEGY environment variable to choose which agent variant runs:
    STRATEGY=baseline   (default — balanced heuristic)
    STRATEGY=offense    (attack-heavy)
    STRATEGY=defense    (turtle / fortress)

All three variants share the same decision pipeline defined in
strategies/base_strategy.py; only the weights and thresholds differ.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

        # Pick strategy variant from environment variable (default: baseline)
        strategy_name = os.environ.get("STRATEGY", "baseline").lower()
        if strategy_name not in STRATEGIES:
            gamelib.debug_write(
                "Unknown strategy '{}', falling back to baseline".format(strategy_name))
            strategy_name = "baseline"

        self.strategy = STRATEGIES[strategy_name]()
        gamelib.debug_write("Using strategy: {}".format(strategy_name))

    def on_game_start(self, config):
        """Read in config and perform any initial setup here."""
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config

    def on_turn(self, turn_state):
        """
        Called every turn.  Delegates all decisions to the active strategy.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write(
            'Performing turn {} of your custom algo strategy'.format(
                game_state.turn_number))
        game_state.suppress_warnings(True)

        # ── Run the modular strategy pipeline ────────────────────────────
        self.strategy.execute_turn(game_state, self.config)

        game_state.submit_turn()

    def on_action_frame(self, turn_string):
        """
        Track where the enemy scores on us and forward to the strategy.
        """
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.strategy.record_breach(location)


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
