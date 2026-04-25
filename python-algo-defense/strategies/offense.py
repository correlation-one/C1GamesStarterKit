"""
offense.py — Offense-focused agent variant.

Compared to baseline:
  • Lower MP threshold  → attacks earlier and more often
  • Skips wall upgrades → saves SP to build supports that buff mobile units
  • Extra support locations for shielding scouts
  • Interceptor stall phase shortened → gets aggressive faster
  • Adds additional scout spawn points to probe more paths
"""

from .base_strategy import BaseStrategy
import gamelib


class OffenseStrategy(BaseStrategy):

    # ── Tuned knobs ──────────────────────────────────────────────────────
    DEFENSE_SP_RATIO        = 0.4       # spend less on defense
    OFFENSE_MP_THRESHOLD    = 6         # attack with less MP (more frequent waves)
    UPGRADE_PRIORITY        = False     # don't bother upgrading walls — save SP
    SUPPORT_ENABLED         = True      # supports buff our mobile units
    INTERCEPTOR_EARLY_TURNS = 3         # shorter stall phase
    SCOUT_RUSH_ENABLED      = True
    DEMOLISHER_LINE_ENABLED = True

    # More support locations to shield our attack waves
    SUPPORT_LOCATIONS = [[13, 2], [14, 2], [13, 3], [14, 3], [12, 2], [15, 2]]

    # Thinner Phase-2 defense — we'd rather spend SP on supports
    TURRET_LOCATIONS_PHASE2 = [[3, 12], [24, 12]]
    WALL_LOCATIONS_PHASE2   = []        # skip extra walls entirely

    # ── Override: more aggressive attack decision ────────────────────────
    def maybe_attack(self, game_state, config, metrics):
        """Offense variant attacks more often and probes multiple paths."""
        SCOUT       = config["unitInformation"][3]["shorthand"]
        DEMOLISHER  = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1

        turn = metrics["turn"]

        # Very short interceptor stall
        if turn < self.INTERCEPTOR_EARLY_TURNS:
            self._stall_with_interceptors(game_state, config)
            return

        # Demolisher line if enemy is stacked at front
        if self.DEMOLISHER_LINE_ENABLED and metrics["enemy_front_units"] > 10:
            self._demolisher_line(game_state, config)
            return

        # Attack most turns (not just every other turn)
        if metrics["my_mp"] >= self.OFFENSE_MP_THRESHOLD:
            # Try all four corner spawn points, pick the safest
            spawn_options = [[13, 0], [14, 0], [0, 13], [27, 13]]
            # Filter to only valid edge locations
            valid = [loc for loc in spawn_options
                     if loc in (game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) +
                                game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT))
                     and not game_state.contains_stationary_unit(loc)]
            if valid:
                best = self._least_damage_spawn(game_state, config, valid)
                game_state.attempt_spawn(SCOUT, best, 1000)
            return

        # Light interceptor patrol while saving up
        self._stall_with_interceptors(game_state, config)
