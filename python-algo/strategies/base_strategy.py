"""
base_strategy.py — Shared decision pipeline for all agent variants.

The pipeline runs in a fixed order every turn:
    1. Evaluate the board  (gather metrics)
    2. Build / upgrade defenses  (using the strategy's defense priorities)
    3. Decide whether to attack  (using the strategy's attack threshold)
    4. Execute the chosen attack  (offense logic)

All behaviour is controlled by a single **aggression** parameter
(0.0 = full defense … 0.5 = balanced … 1.0 = full offense).
The parameter is interpolated into concrete weights so we can sweep
a continuous range of agents for experimentation.
"""

import gamelib
import math


def _lerp(a, b, t):
    """Linear interpolation: a when t=0, b when t=1."""
    return a + (b - a) * t


class BaseStrategy:
    """
    Parameterised agent.  A single `aggression` float (0 → 1) controls
    every knob.  The decision pipeline itself is always the same.

    aggression=0.0  → full defense (turtle)
    aggression=0.5  → balanced (baseline)
    aggression=1.0  → full offense (glass cannon)
    """

    # ── Core defense layout (shared across all aggression levels) ────────
    TURRET_LOCATIONS_PHASE1 = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
    TURRET_LOCATIONS_PHASE2 = [[3, 12], [24, 12], [10, 11], [17, 11]]
    TURRET_LOCATIONS_PHASE3 = [[5, 11], [22, 11]]          # defense-heavy only
    WALL_LOCATIONS_PHASE1   = [[8, 12], [19, 12], [13, 12], [14, 12]]
    WALL_LOCATIONS_PHASE2   = [[1, 13], [26, 13], [3, 13], [24, 13], [7, 12], [20, 12]]
    WALL_LOCATIONS_PHASE3   = [[5, 12], [22, 12], [10, 12], [17, 12]]  # defense-heavy
    SUPPORT_LOCATIONS       = [[13, 2], [14, 2], [13, 3], [14, 3]]
    SUPPORT_LOCATIONS_EXTRA = [[12, 2], [15, 2]]            # offense-heavy (buff waves)

    # ── Initialise per-game state ────────────────────────────────────────
    def __init__(self, aggression=0.5):
        """
        Args:
            aggression: float in [0, 1].
                0.0 = full defense, 0.5 = balanced, 1.0 = full offense.
        """
        self.aggression = max(0.0, min(1.0, aggression))
        self.scored_on_locations = []

        # ── Derived weights (interpolated from aggression) ───────────────
        # MP threshold to attack:  high when defensive, low when offensive
        self.offense_mp_threshold = _lerp(18, 5, self.aggression)
        # Whether to upgrade structures (less likely when offensive)
        self.upgrade_priority = self.aggression < 0.7
        # Whether to build supports (offense wants them to buff waves;
        # defense skips them to spend SP on walls/turrets)
        self.support_enabled = self.aggression > 0.3
        # How many early turns to stall with interceptors
        self.interceptor_early_turns = int(_lerp(8, 2, self.aggression))
        # Whether scout rushes are allowed
        self.scout_rush_enabled = self.aggression > 0.3
        # Whether demolisher line is allowed
        self.demolisher_line_enabled = True
        # How many Phase-2 / Phase-3 defense locations to actually use
        # (offense agents use fewer)
        self._def_phase2_frac = 1.0 - 0.6 * self.aggression
        self._def_phase3_frac = 1.0 - self.aggression

    # ── Public entry point (called by algo_strategy.on_turn) ─────────────
    def execute_turn(self, game_state, config):
        """Fixed pipeline — same for every variant."""
        metrics = self.evaluate_board(game_state, config)
        self.build_defenses(game_state, config, metrics)
        self.maybe_attack(game_state, config, metrics)

    # =====================================================================
    #  STEP 1 — Evaluate the board
    # =====================================================================
    def evaluate_board(self, game_state, config):
        """Gather numbers that later steps use to make decisions."""
        SP = 0
        MP = 1

        my_sp = game_state.get_resource(SP)
        my_mp = game_state.get_resource(MP)
        enemy_health = game_state.enemy_health
        my_health = game_state.my_health

        enemy_front_units = self._count_enemy_units(
            game_state, valid_y=[14, 15]
        )
        enemy_total_structures = self._count_enemy_units(game_state)

        return {
            "turn": game_state.turn_number,
            "my_sp": my_sp,
            "my_mp": my_mp,
            "my_health": my_health,
            "enemy_health": enemy_health,
            "enemy_front_units": enemy_front_units,
            "enemy_total_structures": enemy_total_structures,
        }

    # =====================================================================
    #  STEP 2 — Build / upgrade defenses
    # =====================================================================
    def build_defenses(self, game_state, config, metrics):
        """
        Place turrets, walls, and (optionally) supports.
        Phase 1 always goes first.  The number of Phase 2 / Phase 3
        locations actually built is controlled by _def_phase*_frac,
        which varies with aggression.
        """
        WALL    = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET  = config["unitInformation"][2]["shorthand"]

        # — Phase 1: core turrets + walls (always built) ——————————————
        game_state.attempt_spawn(TURRET, self.TURRET_LOCATIONS_PHASE1)
        game_state.attempt_spawn(WALL,   self.WALL_LOCATIONS_PHASE1)

        if self.upgrade_priority:
            game_state.attempt_upgrade(self.WALL_LOCATIONS_PHASE1)

        # — Reactive defense: turret wherever we got scored on —————————
        self._build_reactive_defense(game_state, config)

        # — Phase 2: additional structures (fraction gated by aggression)
        n2_turrets = max(1, int(len(self.TURRET_LOCATIONS_PHASE2) * self._def_phase2_frac))
        n2_walls   = max(1, int(len(self.WALL_LOCATIONS_PHASE2)   * self._def_phase2_frac))
        game_state.attempt_spawn(TURRET, self.TURRET_LOCATIONS_PHASE2[:n2_turrets])
        game_state.attempt_spawn(WALL,   self.WALL_LOCATIONS_PHASE2[:n2_walls])

        if self.upgrade_priority:
            game_state.attempt_upgrade(self.WALL_LOCATIONS_PHASE2[:n2_walls])
            game_state.attempt_upgrade(self.TURRET_LOCATIONS_PHASE1)

        # — Phase 3: defense-heavy extras (only when aggression is low) —
        if self._def_phase3_frac > 0.0:
            n3_turrets = max(1, int(len(self.TURRET_LOCATIONS_PHASE3) * self._def_phase3_frac))
            n3_walls   = max(1, int(len(self.WALL_LOCATIONS_PHASE3)   * self._def_phase3_frac))
            game_state.attempt_spawn(TURRET, self.TURRET_LOCATIONS_PHASE3[:n3_turrets])
            game_state.attempt_spawn(WALL,   self.WALL_LOCATIONS_PHASE3[:n3_walls])
            if self.upgrade_priority:
                game_state.attempt_upgrade(self.TURRET_LOCATIONS_PHASE3[:n3_turrets])
                game_state.attempt_upgrade(self.WALL_LOCATIONS_PHASE3[:n3_walls])

        # — Supports ——————————————————————————————————————————————————
        if self.support_enabled:
            game_state.attempt_spawn(SUPPORT, self.SUPPORT_LOCATIONS)
            # Offense-heavy agents get extra supports to buff attack waves
            if self.aggression > 0.65:
                game_state.attempt_spawn(SUPPORT, self.SUPPORT_LOCATIONS_EXTRA)

    # =====================================================================
    #  STEP 3 — Decide whether and how to attack
    # =====================================================================
    def maybe_attack(self, game_state, config, metrics):
        """
        Decide between interceptor stall, demolisher line, or scout rush.
        All thresholds derive from the aggression parameter.
        """
        SCOUT       = config["unitInformation"][3]["shorthand"]
        DEMOLISHER  = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1

        turn = metrics["turn"]

        # Early game — stall with interceptors
        if turn < self.interceptor_early_turns:
            self._stall_with_interceptors(game_state, config)
            return

        # Mid / late game decisions
        have_enough_mp = metrics["my_mp"] >= self.offense_mp_threshold

        # If enemy has heavy front, demolisher-line
        if self.demolisher_line_enabled and metrics["enemy_front_units"] > 10:
            self._demolisher_line(game_state, config)
            return

        # If we have enough MP, scout-rush through weakest path
        if self.scout_rush_enabled and have_enough_mp:
            # More aggressive agents attack every turn; balanced every other
            attack_freq = 1 if self.aggression >= 0.7 else 2
            if turn % attack_freq == 1 or self.aggression >= 0.7:
                self._scout_rush(game_state, config)
            return

        # Fallback — light interceptor patrol
        self._stall_with_interceptors(game_state, config)

    # =====================================================================
    #  Attack helpers
    # =====================================================================
    def _scout_rush(self, game_state, config):
        SCOUT = config["unitInformation"][3]["shorthand"]
        spawn_options = [[13, 0], [14, 0]]
        best = self._least_damage_spawn(game_state, config, spawn_options)
        game_state.attempt_spawn(SCOUT, best, 1000)

    def _demolisher_line(self, game_state, config):
        WALL       = config["unitInformation"][0]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        # Build a cheap wall line to keep demolishers at range
        for x in range(27, 5, -1):
            game_state.attempt_spawn(WALL, [x, 11])
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def _stall_with_interceptors(self, game_state, config):
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        edges = (
            game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) +
            game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        )
        deploy = [loc for loc in edges if not game_state.contains_stationary_unit(loc)]
        import random
        while (game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP]
               and deploy):
            loc = deploy[random.randint(0, len(deploy) - 1)]
            game_state.attempt_spawn(INTERCEPTOR, loc)

    # =====================================================================
    #  Reactive defense
    # =====================================================================
    def _build_reactive_defense(self, game_state, config):
        TURRET = config["unitInformation"][2]["shorthand"]
        for location in self.scored_on_locations:
            build_loc = [location[0], location[1] + 1]
            game_state.attempt_spawn(TURRET, build_loc)

    # =====================================================================
    #  Board-analysis helpers
    # =====================================================================
    def _count_enemy_units(self, game_state, unit_type=None,
                           valid_x=None, valid_y=None):
        total = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if (unit.player_index == 1 and
                            (unit_type is None or unit.unit_type == unit_type) and
                            (valid_x is None or location[0] in valid_x) and
                            (valid_y is None or location[1] in valid_y)):
                        total += 1
        return total

    def _least_damage_spawn(self, game_state, config, location_options):
        TURRET = config["unitInformation"][2]["shorthand"]
        damages = []
        for loc in location_options:
            path = game_state.find_path_to_edge(loc)
            damage = 0
            for path_loc in path:
                damage += (len(game_state.get_attackers(path_loc, 0)) *
                           gamelib.GameUnit(TURRET, config).damage_i)
            damages.append(damage)
        return location_options[damages.index(min(damages))]

    # ── Called by algo_strategy.on_action_frame ───────────────────────────
    def record_breach(self, location):
        """Track where the enemy scored on us."""
        self.scored_on_locations.append(location)
