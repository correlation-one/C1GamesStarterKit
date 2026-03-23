import gamelib
import random
import os
import json
from sys import maxsize

from strategies import STRATEGIES, make_strategy


"""
algo_strategy.py — Entry point for the Terminal algo.

Set AGGRESSION to a float 0.0–1.0 for continuous parameter sweep:
    AGGRESSION=0.3   → somewhat defensive

Or set the STRATEGY environment variable to use a named preset:
    STRATEGY=baseline   (default — aggression 0.5)
    STRATEGY=offense    (aggression 0.85)
    STRATEGY=defense    (aggression 0.15)

All variants share the same decision pipeline defined in
strategies/base_strategy.py; only the aggression parameter differs.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

        # ── Pick strategy: AGGRESSION env var takes priority ─────────────
        aggression_str = os.environ.get("AGGRESSION", "")
        if aggression_str:
            aggression = float(aggression_str)
            self.strategy = make_strategy(aggression)
            gamelib.debug_write(
                "Using aggression={:.2f}".format(aggression))
        else:
            strategy_name = os.environ.get("STRATEGY", "baseline").lower()
            if strategy_name not in STRATEGIES:
                gamelib.debug_write(
                    "Unknown strategy '{}', falling back to baseline".format(
                        strategy_name))
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
