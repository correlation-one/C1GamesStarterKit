"""
base_strategy.py — Shared decision pipeline for all agent variants.

The pipeline runs in a fixed order every turn:
    1. Evaluate the board  (gather metrics)
    2. Build / upgrade defenses  (using the strategy's defense priorities)
    3. Decide whether to attack  (using the strategy's attack threshold)
    4. Execute the chosen attack  (offense logic)

Sub-classes override *only* the "knobs" — weight dicts and threshold
methods — so the decision structure stays identical across agents.
"""

import gamelib
import math


class BaseStrategy:
    """
    Abstract-ish base class.  Concrete variants (baseline, offense, defense)
    inherit from this and override the class-level weight constants and/or
    the small helper methods that control behaviour.
    """

    # ── Weights that sub-classes override ────────────────────────────────
    # How much SP to reserve before spending on offense-support structures
    DEFENSE_SP_RATIO = 0.6          # fraction of SP budget for defense
    OFFENSE_MP_THRESHOLD = 10       # minimum MP before launching an attack
    UPGRADE_PRIORITY = True         # whether we upgrade walls before adding more
    SUPPORT_ENABLED = True          # whether we build supports at all
    INTERCEPTOR_EARLY_TURNS = 5     # how many early turns to stall with interceptors
    SCOUT_RUSH_ENABLED = True       # whether we can scout-rush
    DEMOLISHER_LINE_ENABLED = True  # whether we can demolisher-line

    # ── Core defense layout (shared across all variants) ─────────────────
    # Turrets form the backbone; walls shield them.  Supports sit behind.
    # Locations chosen to cover both flanks + middle.
    TURRET_LOCATIONS_PHASE1 = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
    TURRET_LOCATIONS_PHASE2 = [[3, 12], [24, 12], [10, 11], [17, 11]]
    WALL_LOCATIONS_PHASE1   = [[8, 12], [19, 12], [13, 12], [14, 12]]
    WALL_LOCATIONS_PHASE2   = [[1, 13], [26, 13], [3, 13], [24, 13], [7, 12], [20, 12]]
    SUPPORT_LOCATIONS       = [[13, 2], [14, 2], [13, 3], [14, 3]]

    # ── Initialise per-game state ────────────────────────────────────────
    def __init__(self):
        self.scored_on_locations = []

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
        Phase 1 locations always go first; Phase 2 fills in when SP allows.
        """
        WALL    = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET  = config["unitInformation"][2]["shorthand"]

        # — Phase 1: core turrets + walls ——————————————————————
        game_state.attempt_spawn(TURRET, self.TURRET_LOCATIONS_PHASE1)
        game_state.attempt_spawn(WALL,   self.WALL_LOCATIONS_PHASE1)

        if self.UPGRADE_PRIORITY:
            game_state.attempt_upgrade(self.WALL_LOCATIONS_PHASE1)

        # — Reactive defense: place a turret wherever we got scored on ——
        self._build_reactive_defense(game_state, config)

        # — Phase 2: additional structures if we can afford them ————————
        game_state.attempt_spawn(TURRET, self.TURRET_LOCATIONS_PHASE2)
        game_state.attempt_spawn(WALL,   self.WALL_LOCATIONS_PHASE2)

        if self.UPGRADE_PRIORITY:
            game_state.attempt_upgrade(self.WALL_LOCATIONS_PHASE2)
            game_state.attempt_upgrade(self.TURRET_LOCATIONS_PHASE1)

        # — Supports (if enabled by the variant) ——————————————————————
        if self.SUPPORT_ENABLED:
            game_state.attempt_spawn(SUPPORT, self.SUPPORT_LOCATIONS)

    # =====================================================================
    #  STEP 3 — Decide whether and how to attack
    # =====================================================================
    def maybe_attack(self, game_state, config, metrics):
        """
        Decide between interceptor stall, demolisher line, or scout rush.
        The thresholds are tuneable per-variant.
        """
        SCOUT       = config["unitInformation"][3]["shorthand"]
        DEMOLISHER  = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1

        turn = metrics["turn"]

        # Early game — stall with interceptors
        if turn < self.INTERCEPTOR_EARLY_TURNS:
            self._stall_with_interceptors(game_state, config)
            return

        # Mid / late game decisions
        have_enough_mp = metrics["my_mp"] >= self.OFFENSE_MP_THRESHOLD

        # If enemy has heavy front, demolisher-line
        if self.DEMOLISHER_LINE_ENABLED and metrics["enemy_front_units"] > 10:
            self._demolisher_line(game_state, config)
            return

        # If we have enough MP, scout-rush through weakest path
        if self.SCOUT_RUSH_ENABLED and have_enough_mp:
            if turn % 2 == 1:  # every other turn for bigger waves
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
