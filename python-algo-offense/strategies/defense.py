"""
defense.py — Defense-focused agent variant.

Compared to baseline:
  • Higher MP threshold  → only attacks when overwhelmingly resourced
  • Upgrades everything  → walls and turrets are prioritized
  • Extra wall + turret locations to create a fortress
  • Longer interceptor stall phase → turtles early game
  • Scout rush disabled  → conserves MP for interceptors
  • Additional reactive turret placement
"""

from .base_strategy import BaseStrategy
import gamelib


class DefenseStrategy(BaseStrategy):

    # ── Tuned knobs ──────────────────────────────────────────────────────
    DEFENSE_SP_RATIO        = 0.85      # almost all SP goes to defense
    OFFENSE_MP_THRESHOLD    = 18        # only attack when MP is very high
    UPGRADE_PRIORITY        = True      # always upgrade structures
    SUPPORT_ENABLED         = False     # no supports — spend SP on walls/turrets
    INTERCEPTOR_EARLY_TURNS = 8         # longer stall phase
    SCOUT_RUSH_ENABLED      = False     # don't scout rush
    DEMOLISHER_LINE_ENABLED = True      # keep demolisher line as last resort

    # Heavier defense layouts
    TURRET_LOCATIONS_PHASE1 = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
    TURRET_LOCATIONS_PHASE2 = [[3, 12], [24, 12], [10, 11], [17, 11], [5, 11], [22, 11]]
    WALL_LOCATIONS_PHASE1   = [[8, 12], [19, 12], [13, 12], [14, 12]]
    WALL_LOCATIONS_PHASE2   = [[1, 13], [26, 13], [3, 13], [24, 13], [7, 12], [20, 12],
                               [5, 12], [22, 12], [10, 12], [17, 12]]

    # ── Override: much more conservative attack logic ────────────────────
    def maybe_attack(self, game_state, config, metrics):
        """Defense variant turtles and only attacks when it has massive MP."""
        DEMOLISHER  = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1

        turn = metrics["turn"]

        # Long interceptor stall phase
        if turn < self.INTERCEPTOR_EARLY_TURNS:
            self._stall_with_interceptors(game_state, config)
            return

        # Demolisher line if enemy is heavily stacked
        if self.DEMOLISHER_LINE_ENABLED and metrics["enemy_front_units"] > 10:
            self._demolisher_line(game_state, config)
            return

        # Only attack when MP is very high (resources are wasting away)
        if metrics["my_mp"] >= self.OFFENSE_MP_THRESHOLD:
            # Even then, use demolishers for safe ranged damage
            self._demolisher_line(game_state, config)
            return

        # Default: interceptor patrols to defend
        self._stall_with_interceptors(game_state, config)

    # ── Override: extra-aggressive reactive defense ──────────────────────
    def build_defenses(self, game_state, config, metrics):
        """Defense variant also upgrades reactive turrets."""
        # Run the normal defense build
        super().build_defenses(game_state, config, metrics)

        TURRET = config["unitInformation"][2]["shorthand"]
        WALL   = config["unitInformation"][0]["shorthand"]

        # For every breach location, also place a wall in front of the reactive turret
        for location in self.scored_on_locations:
            turret_loc = [location[0], location[1] + 1]
            wall_loc   = [location[0], location[1] + 2]
            game_state.attempt_spawn(WALL, wall_loc)
            game_state.attempt_upgrade(turret_loc)
            game_state.attempt_upgrade(wall_loc)
