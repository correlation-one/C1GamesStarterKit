# Unit type integer IDs — match gamelib constants used by game_state.attempt_spawn
WALL = 0
SUPPORT = 1
TURRET = 2

# ── W-funnel layout coordinates (our side, rows 0–13) ────────────────────────
# Walls are split into two named zones so DefenseManager can apply a
# zone-aware priority order during the early-game layout phase.

# Outer flank walls: guard the board edges, lowest structural priority.
OUTER_WALLS = [
    [0, 13], [1, 12], [2, 11],    # left outer arm
    [25, 11], [26, 12], [27, 13], # right outer arm
]

# Inner funnel walls: angled segments that converge enemy paths toward turrets.
INNER_WALLS = [
    [6, 9],  [7, 10],  [8, 11],          # left inner shoulder
    [12, 9], [13, 10], [14, 10], [15, 9], # centre bridge
    [19, 11], [20, 10], [21, 9],           # right inner shoulder
]

# Combined list (inner first, then outer) — used by EconomyController's SP queue.
W_FUNNEL_WALLS = INNER_WALLS + OUTER_WALLS

# Turrets sit at each choke point created by the W walls — highest SP priority.
W_FUNNEL_TURRETS = [
    [3, 11], [24, 11],  # outer kill zones
    [9, 9],  [18, 9],   # inner kill zones
    [13, 8], [14, 8],   # centre kill zone
]

# ── Priority order for the early-game layout phase ───────────────────────────
# Turrets first (highest value per SP), then inner funnel walls, then outer walls.
_LAYOUT_ORDER = (
    [(TURRET, loc) for loc in W_FUNNEL_TURRETS] +
    [(WALL,   loc) for loc in INNER_WALLS] +
    [(WALL,   loc) for loc in OUTER_WALLS]
)

# Number of turns spent in the forced layout phase (turns 0 … LAYOUT_TURNS-1).
LAYOUT_TURNS = 5


class DefenseManager:
    def __init__(self):
        pass

    # Board bounds for our half (player 0 occupies rows 0–13, columns 0–27).
    _BOARD_X_MIN = 0
    _BOARD_X_MAX = 27
    _BOARD_Y_MIN = 0
    _BOARD_Y_MAX = 13

    def build(self, game_state, decision, state_memory=None):
        """Place or upgrade structures according to the current turn phase.

        Reactive patching (all turns):
            For every breach coordinate recorded in ``state_memory.breach_locations``
            a turret is attempted at ``[breach_x, breach_y + 1]`` if the tile is
            empty and within our half of the board.  This runs *before* the main
            layout or queue logic so breach reinforcement has first claim on SP.

        Layout phase (turns 0–LAYOUT_TURNS-1):
            Spend all available SP on the W-funnel in priority order:
            turrets → inner walls → outer walls.  Each tile is skipped when
            `game_state.contains_stationary_unit()` already returns True so
            that `attempt_spawn()` is never called redundantly.

        Queue phase (turn LAYOUT_TURNS onward):
            Execute the ordered build_queue produced by EconomyController.
            ``'place'`` actions are skipped when the tile is already occupied;
            ``'upgrade'`` actions are forwarded directly (the queue was already
            screened for unupgraded units by EconomyController).

        Path-based restructuring (all turns, after main SP spend):
            For each breach coordinate recorded ≥ 2 times, walk
            ``state_memory.last_breach_path`` from the enemy edge inward to
            find the earliest unoccupied tile in our buildable half.  The
            wall(s) at/adjacent to the old breach point are queued for removal
            and a new wall is placed at the intercept tile, forcing a longer
            enemy path on the next attack.
        """
        self._apply_breach_patches(game_state, state_memory)
        if game_state.turn_number < LAYOUT_TURNS:
            self._build_layout(game_state)
        else:
            self._execute_queue(game_state, decision)
        self._apply_path_restructuring(game_state, state_memory)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_breach_patches(self, game_state, state_memory):
        """Attempt to place a turret one row above each recorded breach point.

        Runs every turn before the main layout/queue logic so that breach
        reinforcement has first claim on available SP.  Idempotency is
        guaranteed by the `contains_stationary_unit()` guard — no redundant
        spawn call is ever made.  Coordinates outside the player's half of the
        board (y > _BOARD_Y_MAX after +1) are silently skipped.
        """
        if state_memory is None:
            return
        breach_locations = getattr(state_memory, 'breach_locations', {})
        if not breach_locations:
            return
        for (breach_x, breach_y) in breach_locations:
            patch_x = breach_x
            patch_y = breach_y + 1
            # Validate patch target is within our half of the board.
            if not (self._BOARD_X_MIN <= patch_x <= self._BOARD_X_MAX):
                continue
            if not (self._BOARD_Y_MIN <= patch_y <= self._BOARD_Y_MAX):
                continue
            patch_target = [patch_x, patch_y]
            if not game_state.contains_stationary_unit(patch_target):
                game_state.attempt_spawn(TURRET, patch_target)

    def _apply_path_restructuring(self, game_state, state_memory):
        """Restructure defences when a breach coordinate has been hit ≥ 2 times.

        For each such coordinate the method walks ``state_memory.last_breach_path``
        from index 0 (enemy edge) toward our edge, looking for the first tile
        that satisfies all three conditions:

            a. ``tile[1] < 14`` — within our buildable half of the board.
            b. ``not game_state.contains_stationary_unit(tile)`` — unoccupied.
            c. Sufficient SP to place a wall (≥ 0.5 SP remaining).

        When a qualifying intercept tile is found:
            1. ``attempt_remove()`` is called on the breach point and its
               vertically adjacent tiles so the old chokepoint is dismantled.
            2. ``attempt_spawn(WALL, intercept_tile)`` plants the new wall
               closer to the enemy edge, forcing a longer path next time.

        Guards: returns immediately for None/missing ``state_memory``, an empty
        ``breach_locations`` dict, no repeat breaches (count < 2), an empty or
        None ``last_breach_path``, or when no qualifying tile can be found.
        """
        if state_memory is None:
            return
        breach_locations = getattr(state_memory, 'breach_locations', {})
        if not breach_locations:
            return
        # Collect breach coordinates that have been hit 2 or more times.
        repeat_breaches = [
            (coord, count)
            for coord, count in breach_locations.items()
            if count >= 2
        ]
        if not repeat_breaches:
            return
        last_breach_path = getattr(state_memory, 'last_breach_path', None)
        if not last_breach_path:
            return

        for (breach_x, breach_y), _count in repeat_breaches:
            # Walk path from enemy edge (index 0) toward our edge.
            intercept_tile = None
            for tile in last_breach_path:
                # Expect each tile to be a sequence of at least [x, y].
                if not isinstance(tile, (list, tuple)) or len(tile) < 2:
                    continue
                tx, ty = int(tile[0]), int(tile[1])
                # (a) Must be within our buildable half.
                if ty >= 14:
                    continue
                # (b) Must not already be occupied by a structure.
                if game_state.contains_stationary_unit([tx, ty]):
                    continue
                # (c) Must have enough SP to place at least one wall.
                if game_state.get_resource(game_state.SP, 0) < 0.5:
                    break  # No SP remaining — skip remaining tiles too.
                intercept_tile = [tx, ty]
                break

            if intercept_tile is None:
                # No valid intercept tile found along the path for this breach.
                continue

            # Queue removal of the old breach point and its vertical neighbours
            # so the existing chokepoint is dismantled before the new wall goes up.
            game_state.attempt_remove([breach_x, breach_y])
            for adj_y in (breach_y - 1, breach_y + 1):
                if self._BOARD_Y_MIN <= adj_y <= self._BOARD_Y_MAX:
                    game_state.attempt_remove([breach_x, adj_y])

            # Place the new intercepting wall at the earliest qualifying tile.
            game_state.attempt_spawn(WALL, intercept_tile)

    def _build_layout(self, game_state):
        """Early-game phase: place W-funnel structures in priority order."""
        for unit_type, loc in _LAYOUT_ORDER:
            if not game_state.contains_stationary_unit(loc):
                game_state.attempt_spawn(unit_type, loc)

    def _execute_queue(self, game_state, decision):
        """Queue phase: execute EconomyController's ordered build list."""
        if not decision:
            return
        build_queue = decision.get('build_queue', [])
        for action in build_queue:
            loc = action.get('location')
            unit_type = action.get('type')
            act = action.get('action')
            if loc is None or unit_type is None or act is None:
                continue
            if act == 'place':
                if not game_state.contains_stationary_unit(loc):
                    game_state.attempt_spawn(unit_type, loc)
            elif act == 'upgrade':
                game_state.attempt_spawn(unit_type, loc)
