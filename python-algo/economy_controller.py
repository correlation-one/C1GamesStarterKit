from defense_manager import (
    WALL, SUPPORT, TURRET,
    OUTER_WALLS, INNER_WALLS,
    W_FUNNEL_WALLS, W_FUNNEL_TURRETS,
)

# Fixed support tile coordinates (low-priority quality-of-life placements).
_SUPPORT_LOCATIONS = [[13, 2], [14, 2], [13, 3], [14, 3]]

# Ordered list of (unit_type, location) pairs for the W-funnel placement tier.
_FUNNEL_PLACEMENTS = (
    [(WALL, loc) for loc in W_FUNNEL_WALLS] +
    [(TURRET, loc) for loc in W_FUNNEL_TURRETS]
)


def _tile_has_unit(game_state, unit_type, loc):
    """Return True if our player already has *unit_type* at *loc*."""
    try:
        units = game_state.game_map[loc]
        return bool(units and units[0].player_index == 0 and units[0].unit_type == unit_type)
    except Exception:
        return False


def _place_cost(game_state, unit_type):
    """SP cost to place *unit_type*; returns 0.0 on any error."""
    try:
        return float(game_state.type_cost(unit_type)[game_state.SP])
    except Exception:
        return 0.0


def _upgrade_cost(game_state, unit_type):
    """Additional SP cost to upgrade *unit_type*; returns 0.0 on any error."""
    try:
        return float(
            game_state.type_cost(unit_type, upgrade=True)[game_state.SP]
            - game_state.type_cost(unit_type)[game_state.SP]
        )
    except Exception:
        return 0.0


class EconomyController:
    def __init__(self):
        self.mp_attack_threshold = 10

    def decide(self, game_state, threat):
        try:
            current_mp = game_state.get_resource(game_state.MP, 0)
            projected_mp = game_state.project_future_MP(1, 0)
            enemy_health = game_state.enemy_health

            attack_this_turn = (
                current_mp >= self.mp_attack_threshold
                or projected_mp < current_mp * 0.9
                or enemy_health <= 5
            )
        except Exception:
            attack_this_turn = False

        build_queue = self._build_sp_queue(game_state)

        return {'attack_this_turn': attack_this_turn, 'build_queue': build_queue}

    # ------------------------------------------------------------------
    # SP build-priority queue
    # ------------------------------------------------------------------

    def _build_sp_queue(self, game_state):
        """Return an ordered list of build-action dicts for DefenseManager.

        Each dict has the keys:
            ``type``     – integer unit type constant (WALL / SUPPORT / TURRET)
            ``location`` – [x, y] board coordinate
            ``action``   – ``'place'`` or ``'upgrade'``

        The list is ordered by descending priority:
          1. W-funnel placements not yet present in game_state
          2. Turret upgrades (sorted by location for determinism)
          3. Wall upgrades   (sorted by location for determinism)
          4. Support placements not yet present in game_state

        Actions are appended until their cumulative SP cost would exceed the
        available SP; subsequent items in the same turn cannot be afforded so
        they are omitted.  DefenseManager.build() executes the list in order
        and stops naturally when SP is exhausted.
        """
        try:
            available_sp = float(game_state.get_resource(game_state.SP, 0))
        except Exception:
            return []

        actions = []
        cumulative = 0.0

        def _append(unit_type, loc, act, cost):
            """Add action to the queue; return False when budget is exceeded."""
            nonlocal cumulative
            cumulative += cost
            if cumulative > available_sp:
                return False
            actions.append({"type": unit_type, "location": list(loc), "action": act})
            return True

        # ── Priority 1: W-funnel placements ──────────────────────────────
        for unit_type, loc in _FUNNEL_PLACEMENTS:
            if not _tile_has_unit(game_state, unit_type, loc):
                cost = _place_cost(game_state, unit_type)
                if not _append(unit_type, loc, "place", cost):
                    return actions

        # ── Priority 2: Turret upgrades ───────────────────────────────────
        turret_upgrade_locs = []
        try:
            for loc in game_state.game_map:
                units = game_state.game_map[loc]
                if (units
                        and units[0].player_index == 0
                        and units[0].unit_type == TURRET
                        and not units[0].upgraded):
                    turret_upgrade_locs.append(list(loc))
        except Exception:
            pass
        turret_upgrade_locs.sort()
        for loc in turret_upgrade_locs:
            cost = _upgrade_cost(game_state, TURRET)
            if not _append(TURRET, loc, "upgrade", cost):
                return actions

        # ── Priority 3: Wall upgrades ─────────────────────────────────────
        wall_upgrade_locs = []
        try:
            for loc in game_state.game_map:
                units = game_state.game_map[loc]
                if (units
                        and units[0].player_index == 0
                        and units[0].unit_type == WALL
                        and not units[0].upgraded):
                    wall_upgrade_locs.append(list(loc))
        except Exception:
            pass
        wall_upgrade_locs.sort()
        for loc in wall_upgrade_locs:
            cost = _upgrade_cost(game_state, WALL)
            if not _append(WALL, loc, "upgrade", cost):
                return actions

        # ── Priority 4: Support placements ────────────────────────────────
        for loc in _SUPPORT_LOCATIONS:
            if not _tile_has_unit(game_state, SUPPORT, loc):
                cost = _place_cost(game_state, SUPPORT)
                if not _append(SUPPORT, loc, "place", cost):
                    return actions

        return actions
