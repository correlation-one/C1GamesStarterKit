import math

# Unit type integer constants (mirrors gamelib.unit.UnitType values)
_WALL       = 0
_SUPPORT    = 1
_TURRET     = 2
_SCOUT      = 3
_DEMOLISHER = 4

# Persistence weights for enemy structures
_PERSISTENCE = {_SUPPORT: 3, _TURRET: 2, _WALL: 1}

# Attack ranges by unit type
_ATTACK_RANGE = {_SCOUT: 3.5, _DEMOLISHER: 4.5}
_DEFAULT_RANGE = 3.5

# Board bounds
_BOARD_MIN = 0
_BOARD_MAX = 27

# Turret base damage per frame (approximation used by the survival scorer)
_TURRET_DAMAGE = 6.0

# Lateral-side boundary: x < _SIDE_BOUNDARY → left, x >= _SIDE_BOUNDARY → right
_SIDE_BOUNDARY = 14

# Lambda auto-adjustment constants
_LAMBDA_MAE_GATE   = 2.0   # skip adjustment if MAE between prediction and actual exceeds this
_LAMBDA_MIN        = 0.15  # lower bound on current_lambda after adjustment
_LAMBDA_MAX        = 0.70  # upper bound on current_lambda after adjustment
_LAMBDA_STEP       = 0.05  # magnitude of each per-entry nudge
_LAMBDA_MIN_BUFFER = 4     # minimum buffer entries before adjustment is attempted
_SVD_NEAR_ZERO     = 0.5   # structure_value_destroyed below this is treated as approximately zero
_BREACH_NEAR_ZERO  = 1     # edge_breaches below this (i.e. == 0) is treated as approximately zero


def _lateral_side(tile):
    """Return ``'left'`` or ``'right'`` based on the tile's x coordinate."""
    return "left" if int(tile[0]) < _SIDE_BOUNDARY else "right"


def _collect_demo_target_tiles(game_state, spawn):
    """Return the locations of enemy structures within demolisher range along *spawn*'s path.

    These tiles represent the gap that the demolisher may have opened.  On the
    following scout turn they are rechecked via ``contains_stationary_unit`` to
    determine whether the enemy has rebuilt.

    Args:
        game_state: Current ``GameState`` object.
        spawn:      Demolisher spawn location ([x, y]).

    Returns:
        List of ``[x, y]`` positions of enemy structures that were in demolisher
        attack range during the turn.  Empty list if the path cannot be computed.
    """
    try:
        path = game_state.find_path_to_edge(spawn)
    except Exception:
        return []
    if not path:
        return []

    attack_range = _ATTACK_RANGE[_DEMOLISHER]
    range_sq = attack_range ** 2
    radius = int(math.ceil(attack_range))

    seen = set()
    target_tiles = []

    for tile in path:
        tx, ty = int(tile[0]), int(tile[1])
        x_lo = max(_BOARD_MIN, tx - radius)
        x_hi = min(_BOARD_MAX, tx + radius)
        y_lo = max(_BOARD_MIN, ty - radius)
        y_hi = min(_BOARD_MAX, ty + radius)

        for lx in range(x_lo, x_hi + 1):
            for ly in range(y_lo, y_hi + 1):
                if (lx - tx) ** 2 + (ly - ty) ** 2 > range_sq:
                    continue
                key = (lx, ly)
                if key in seen:
                    continue
                seen.add(key)
                try:
                    unit = game_state.contains_stationary_unit([lx, ly])
                except Exception:
                    unit = None
                if unit is not None and getattr(unit, "player_index", -1) == 1:
                    target_tiles.append([lx, ly])

    return target_tiles

# Default shield granted per support unit per unit shielded.
# Source: Terminal SDK gamelib/unit.py — UnitType.SUPPORT shieldPerUnit = 3.
_DEFAULT_SUPPORT_SHIELD = 3.0


class AttackPlanner:
    def __init__(self):
        pass

    def plan_and_execute(self, game_state, decision, state_memory=None):
        """Plan and execute an attack for the current turn.

        The method determines the attack *mode* (``'scout'`` or
        ``'demolisher'``) once from *decision* and derives **all** unit
        statistics exclusively from that mode.  The same mode value is
        propagated to every downstream phase without re-evaluation:

        1. Unit-stat resolution (type, HP, damage)  ← mode-conditional block
        2. Shortlist scoring                         ← receives ``unit_type``
        3. Frame simulation                          ← receives ``unit_type``
           and ``unit_damage``
        4. Spawn selection                           ← receives
           ``is_demolisher_turn``

        Args:
            game_state:   Current ``GameState`` object.
            decision:     Dict returned by ``EconomyController.decide()``.
                          Expected keys:
                          - ``"attack_this_turn"`` (bool)
                          - ``"attack_type"``      (``'scout'`` |
                            ``'demolisher'``; defaults to ``'scout'``)
            state_memory: Optional ``StateMemory`` instance.  When supplied
                          ``current_lambda`` is read from it for the composite
                          scorer; when ``None`` the scorer falls back to the
                          built-in default (0.4).
        """
        # ── Step 0: snapshot demolisher-push bridge state ─────────────────────
        # Read before any evaluation so the flag reflects the *previous* turn.
        _last_was_demo = (
            state_memory is not None
            and getattr(state_memory, "last_turn_was_demolisher_push", False)
        )
        _demo_target_tiles = (
            list(getattr(state_memory, "demolisher_target_tiles", []))
            if _last_was_demo else []
        )

        # ── Step 1: determine mode — resolved once, never re-evaluated ────────
        attack_type      = decision.get("attack_type", "scout")
        mode             = "demolisher" if attack_type == "demolisher" else "scout"
        is_demolisher_turn = (mode == "demolisher")

        if not decision.get("attack_this_turn", False):
            return

        # ── Step 2: derive unit type and stats exclusively from mode ──────────
        # No unit-stat constants appear outside this conditional block.
        if is_demolisher_turn:
            unit_type = _DEMOLISHER
            try:
                ui          = game_state.config["unitInformation"][_DEMOLISHER]
                unit_hp     = float(ui.get("startHealth", 5.0))
                unit_damage = float(ui.get("attackDamageTower", 8.0))
            except Exception:
                unit_hp, unit_damage = 5.0, 8.0
        else:  # scout
            unit_type = _SCOUT
            try:
                ui          = game_state.config["unitInformation"][_SCOUT]
                unit_hp     = float(ui.get("startHealth", 15.0))
                unit_damage = float(ui.get("attackDamageTower", 2.0))
            except Exception:
                unit_hp, unit_damage = 15.0, 2.0

        # ── Step 3: how many units can we afford this turn? ───────────────────
        try:
            mp        = float(game_state.get_resource(game_state.MP, 0))
            unit_cost = float(game_state.type_cost(unit_type)[game_state.MP])
            unit_count = int(mp // unit_cost) if unit_cost > 0 else 0
        except Exception:
            unit_count = 0

        if unit_count <= 0:
            return

        # ── Step 4: enumerate candidate spawn locations ───────────────────────
        try:
            edges = (
                game_state.game_map.get_edge_locations(
                    game_state.game_map.BOTTOM_LEFT
                ) +
                game_state.game_map.get_edge_locations(
                    game_state.game_map.BOTTOM_RIGHT
                )
            )
        except Exception:
            return

        # ── Sequential composition bridge ─────────────────────────────────────
        # When this is a scout turn immediately following a demolisher push,
        # check whether the gap the demolisher opened is still exploitable.
        spawn_candidates = list(edges)
        if not is_demolisher_turn and _last_was_demo and _demo_target_tiles:
            # Identify which demolished tiles the enemy has not yet rebuilt.
            open_tiles = [
                t for t in _demo_target_tiles
                if not game_state.contains_stationary_unit(t)
            ]
            if open_tiles:
                # Gap is still open — restrict spawns to the matching lateral side.
                avg_x = sum(int(t[0]) for t in open_tiles) / len(open_tiles)
                gap_side = "left" if avg_x < _SIDE_BOUNDARY else "right"
                filtered = [s for s in spawn_candidates if _lateral_side(s) == gap_side]
                if filtered:  # only apply restriction if it leaves at least one candidate
                    spawn_candidates = filtered
            # If all tiles are rebuilt (open_tiles is empty), spawn_candidates
            # stays as the full edge list — full evaluation, no bias.

        # ── Step 5: shortlist phase — unit_type derived from mode ─────────────
        scored_locations = []
        for spawn in spawn_candidates:
            try:
                path = game_state.find_path_to_edge(spawn)
            except Exception:
                path = None
            if not path:
                continue

            weighted_structure_hp_sum = self.compute_structure_density(
                game_state, path, unit_type
            )
            survival_weighted_damage_taken, _ = self.compute_survival_weighted_score(
                game_state, path, unit_hp, unit_count, unit_type
            )
            scored_locations.append({
                "spawn":                          list(spawn),
                "survival_weighted_damage_taken": survival_weighted_damage_taken,
                "weighted_structure_hp_sum":      weighted_structure_hp_sum,
            })

        if not scored_locations:
            return

        shortlist = self.select_shortlist(scored_locations)
        if not shortlist:
            return

        # ── Step 6: frame simulation — unit stats from mode ───────────────────
        sim_candidates = []
        for entry in shortlist:
            spawn = entry["spawn"]
            try:
                path = game_state.find_path_to_edge(spawn)
            except Exception:
                path = None
            if not path:
                continue

            result = self._simulate_frames(
                game_state, path, unit_count, unit_hp, unit_damage, unit_type
            )
            result["spawn"] = spawn
            sim_candidates.append(result)

        if not sim_candidates:
            return

        # ── Step 7: scorer — is_demolisher_turn from mode ────────────────────
        best_spawn, _best_score, frame_sim_prediction = self._select_best_spawn(
            sim_candidates, state_memory, is_demolisher_turn
        )

        if best_spawn is None:
            return

        # ── Capture lambda_used before spawning (reflects decision-time value) ─
        lambda_used = float(getattr(state_memory, "current_lambda", 0.4)) if state_memory is not None else 0.4

        # ── Step 8: spawn the attacking units ─────────────────────────────────
        try:
            game_state.attempt_spawn(unit_type, best_spawn, unit_count)
        except Exception as exc:
            print(f"[AttackPlanner] attempt_spawn failed: {exc}")

        # ── Bridge state update ───────────────────────────────────────────────
        # Demolisher turn: record which enemy-structure tiles were in range so
        # the following scout turn can test whether the gap is still open.
        # Scout turn: always clear the flag regardless of which branch ran,
        # so it cannot persist past this turn.
        if state_memory is not None:
            if is_demolisher_turn:
                target_tiles = _collect_demo_target_tiles(game_state, best_spawn)
                state_memory.set_demolisher_push(target_tiles)
            else:
                state_memory.clear_demolisher_push()

        # ── Outcome recording ─────────────────────────────────────────────────
        # Assembles a structured entry for every attack turn (scout and
        # demolisher alike) and writes it to the rolling outcome buffer.
        # Breach and structure-destruction data come from StateMemory's
        # action-frame aggregation (populated by on_action_frame() during the
        # most recently resolved combat phase).
        if state_memory is not None:
            edge_breaches = int(getattr(state_memory, "turn_breach_count", 0))
            structure_value_destroyed = float(
                getattr(state_memory, "turn_structure_value_destroyed", 0.0)
            )
            outcome_entry = {
                "lambda_used":               lambda_used,
                "edge_breaches":             edge_breaches,
                "structure_value_destroyed": structure_value_destroyed,
                "frame_sim_prediction":      frame_sim_prediction,
            }
            state_memory.record_attack_outcome(outcome_entry)
            self._adjust_lambda(state_memory)

    def _adjust_lambda(self, state_memory):
        """Nudge ``StateMemory.current_lambda`` based on recent attack outcomes.

        Reads the rolling outcome buffer and applies a bounded adjustment to
        ``current_lambda`` when the frame simulation has been accurate (MAE ≤
        ``_LAMBDA_MAE_GATE``) and recent consecutive outcomes show a consistent
        skew between edge breaches and structure-value destroyed.

        The adjustment is skipped entirely when:

        - ``state_memory`` is ``None``
        - The buffer contains fewer than ``_LAMBDA_MIN_BUFFER`` entries
        - MAE between ``frame_sim_prediction`` and ``edge_breaches`` exceeds
          ``_LAMBDA_MAE_GATE`` (sim fidelity too low)

        When the trailing consecutive run signals a consistent skew the lambda
        is nudged by ``_LAMBDA_STEP`` **per qualifying entry** in the run, then
        clamped to ``[_LAMBDA_MIN, _LAMBDA_MAX]``.

        - Down (lambda over-weights structure): consecutive entries where
          ``structure_value_destroyed < _SVD_NEAR_ZERO`` *and*
          ``edge_breaches ≥ _BREACH_NEAR_ZERO``.
        - Up (lambda under-weights structure): consecutive entries where
          ``edge_breaches < _BREACH_NEAR_ZERO`` *and*
          ``structure_value_destroyed ≥ _SVD_NEAR_ZERO``.

        Args:
            state_memory: ``StateMemory`` instance (may be ``None``).
        """
        if state_memory is None:
            return

        buffer = state_memory.get_outcome_buffer()
        if len(buffer) < _LAMBDA_MIN_BUFFER:
            return

        # ------------------------------------------------------------------
        # Accuracy gate: compute MAE between frame-sim prediction and actual
        # edge breaches across the full buffer.
        # ------------------------------------------------------------------
        mae = sum(
            abs(e["frame_sim_prediction"] - e["edge_breaches"]) for e in buffer
        ) / len(buffer)

        if mae > _LAMBDA_MAE_GATE:
            return  # sim fidelity too low — do not modify lambda

        # ------------------------------------------------------------------
        # Trailing consecutive run detection.
        # Walk from the most-recent entry backward, counting entries that
        # uniformly exhibit the same directional skew.  The first entry whose
        # skew differs (or has no skew) terminates the run.
        # ------------------------------------------------------------------
        down_run = 0  # consecutive: structure_value_destroyed ≈ 0, breaches high
        up_run   = 0  # consecutive: edge_breaches ≈ 0, structure_value high

        for entry in reversed(buffer):
            svd      = entry["structure_value_destroyed"]
            breaches = entry["edge_breaches"]

            is_down = svd < _SVD_NEAR_ZERO and breaches >= _BREACH_NEAR_ZERO
            is_up   = breaches < _BREACH_NEAR_ZERO and svd >= _SVD_NEAR_ZERO

            if down_run == 0 and up_run == 0:
                # First (most recent) entry sets the direction
                if is_down:
                    down_run = 1
                elif is_up:
                    up_run = 1
                else:
                    break  # most recent entry shows no skew — no adjustment
            elif down_run > 0:
                if is_down:
                    down_run += 1
                else:
                    break
            else:  # up_run > 0
                if is_up:
                    up_run += 1
                else:
                    break

        # ------------------------------------------------------------------
        # Apply nudge proportional to run length, then clamp to valid range.
        # ------------------------------------------------------------------
        if down_run == 0 and up_run == 0:
            return  # no skew detected

        current = float(getattr(state_memory, "current_lambda", 0.4))

        if down_run > 0:
            current -= _LAMBDA_STEP * down_run
        else:
            current += _LAMBDA_STEP * up_run

        state_memory.current_lambda = max(_LAMBDA_MIN, min(_LAMBDA_MAX, current))

    def compute_structure_density(self, game_state, path, unit_type):
        """Return the weighted HP sum of enemy structures encountered along *path*.

        For each tile in the path the method collects all enemy stationary
        structures within Euclidean attack range of that tile.  Each structure
        is counted **once** (at the first path tile where it enters range) to
        avoid double-counting.  The accumulated value is:

            sum( persistence_weight(unit) * unit.health )

        where persistence weights are: support ×3, turret ×2, wall ×1.

        Args:
            game_state: Current GameState object.
            path:       List of [x, y] tiles (e.g. from game_state.find_path_to_edge).
            unit_type:  Integer unit-type constant (3 = scout, 4 = demolisher).

        Returns:
            weighted_structure_hp_sum as a float.
        """
        if not path:
            return 0.0

        attack_range = _ATTACK_RANGE.get(unit_type, _DEFAULT_RANGE)
        range_sq = attack_range ** 2
        radius = int(math.ceil(attack_range))

        seen = set()          # (lx, ly) locations already counted
        weighted_hp_sum = 0.0

        for tile in path:
            tx, ty = int(tile[0]), int(tile[1])

            x_lo = max(_BOARD_MIN, tx - radius)
            x_hi = min(_BOARD_MAX, tx + radius)
            y_lo = max(_BOARD_MIN, ty - radius)
            y_hi = min(_BOARD_MAX, ty + radius)

            for lx in range(x_lo, x_hi + 1):
                for ly in range(y_lo, y_hi + 1):
                    # Respect exact Euclidean range
                    if (lx - tx) ** 2 + (ly - ty) ** 2 > range_sq:
                        continue

                    key = (lx, ly)
                    if key in seen:
                        continue
                    seen.add(key)

                    units = game_state.game_map[lx, ly]
                    if not units:
                        continue

                    for unit in units:
                        if not unit.stationary or unit.player_index != 1:
                            continue
                        weight = _PERSISTENCE.get(unit.unit_type, 1)
                        weighted_hp_sum += weight * unit.health

        return weighted_hp_sum

    def compute_survival_weighted_score(self, game_state, path, unit_hp, unit_count, unit_type):
        """Compute survival-weighted signals for a single spawn path.

        Walks the path tile-by-tile, accumulating damage dealt by enemy turrets
        and discounting enemy structure value by the probability that units are
        still alive at each point.

        Args:
            game_state: Current GameState object.
            path:       List of [x, y] tiles in traversal order.
            unit_hp:    Base HP of each attacking unit.
            unit_count: Number of attacking units.
            unit_type:  Integer unit-type constant (3 = scout, 4 = demolisher).

        Returns:
            Tuple ``(survival_weighted_damage_taken, survival_weighted_structure_value)``:
            - ``survival_weighted_damage_taken``: raw cumulative damage received
              along the path (lower → safer path, used for sorting).
            - ``survival_weighted_structure_value``: weighted enemy structure HP
              along the path, discounted by survival probability at each tile
              (higher → more valuable target path).
        """
        total_hp_pool = unit_hp * unit_count

        if total_hp_pool <= 0.0:
            return 0.0, 0.0

        attack_range = _ATTACK_RANGE.get(unit_type, _DEFAULT_RANGE)
        range_sq = attack_range ** 2
        radius = int(math.ceil(attack_range))

        cumulative_damage = 0.0
        survival_weighted_structure_value = 0.0
        seen = set()  # (lx, ly) locations already credited to structure value

        for tile in path:
            tx, ty = int(tile[0]), int(tile[1])

            # --- Damage from turrets attacking units at this tile ---
            try:
                attackers = game_state.get_attackers(tile, 0)
            except Exception:
                attackers = []

            frame_damage = len(attackers) * _TURRET_DAMAGE
            cumulative_damage += frame_damage

            # Survival probability after damage received through this tile
            survival_probability = max(0.0, 1.0 - cumulative_damage / total_hp_pool)

            # --- Enemy structure value in attack range of this tile ---
            x_lo = max(_BOARD_MIN, tx - radius)
            x_hi = min(_BOARD_MAX, tx + radius)
            y_lo = max(_BOARD_MIN, ty - radius)
            y_hi = min(_BOARD_MAX, ty + radius)

            for lx in range(x_lo, x_hi + 1):
                for ly in range(y_lo, y_hi + 1):
                    if (lx - tx) ** 2 + (ly - ty) ** 2 > range_sq:
                        continue

                    key = (lx, ly)
                    if key in seen:
                        continue
                    seen.add(key)

                    units = game_state.game_map[lx, ly]
                    if not units:
                        continue

                    for unit in units:
                        if not unit.stationary or unit.player_index != 1:
                            continue
                        weight = _PERSISTENCE.get(unit.unit_type, 1)
                        survival_weighted_structure_value += (
                            weight * unit.health * survival_probability
                        )

        return cumulative_damage, survival_weighted_structure_value

    def select_shortlist(self, scored_locations):
        """Select 3–5 candidate spawn locations for the frame simulation.

        Uses two signals to build the shortlist:
        1. **Density signal** – locations whose ``weighted_structure_hp_sum``
           falls in the top quartile (above the 75th-percentile threshold) are
           unconditionally included regardless of how dangerous the path is.
        2. **Safety signal** – from the remaining candidates the safest paths
           (lowest ``survival_weighted_damage_taken``) fill the list to a
           maximum of 5 entries.

        The shortlist is guaranteed to have at least 3 entries as long as the
        input contains at least 3 candidates.  If the input has fewer than 3
        entries all of them are returned unchanged.

        Args:
            scored_locations: List of dicts, each with keys:
                - ``spawn`` ([x, y] coords)
                - ``survival_weighted_damage_taken`` (float, lower = safer)
                - ``weighted_structure_hp_sum``      (float, higher = more value)

        Returns:
            List of dicts (same schema as input) with between 3 and 5 entries,
            or all entries when fewer than 3 were supplied.
        """
        if not scored_locations:
            return []

        # Fast path: fewer candidates than the minimum shortlist size
        if len(scored_locations) <= 3:
            return list(scored_locations)

        # ------------------------------------------------------------------
        # 1. Compute 75th-percentile threshold via linear interpolation
        # ------------------------------------------------------------------
        hp_values = sorted(
            entry["weighted_structure_hp_sum"] for entry in scored_locations
        )
        n = len(hp_values)
        idx = 0.75 * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        threshold = hp_values[lo] + frac * (hp_values[hi] - hp_values[lo])

        # ------------------------------------------------------------------
        # 2. Partition: unconditionally included vs. remaining candidates
        # ------------------------------------------------------------------
        high_density = []
        remaining = []
        for entry in scored_locations:
            if entry["weighted_structure_hp_sum"] > threshold:
                high_density.append(entry)
            else:
                remaining.append(entry)

        # Deterministic ordering: high-density by value desc, then spawn coords
        high_density.sort(
            key=lambda e: (
                -e["weighted_structure_hp_sum"],
                e["spawn"][0],
                e["spawn"][1],
            )
        )

        # Remaining ordered safest-first (damage asc), then spawn coords for ties
        remaining.sort(
            key=lambda e: (
                e["survival_weighted_damage_taken"],
                e["spawn"][0],
                e["spawn"][1],
            )
        )

        # ------------------------------------------------------------------
        # 3. Build shortlist: unconditional entries first, then safest fillers
        # ------------------------------------------------------------------
        _SHORTLIST_MAX = 5
        _SHORTLIST_MIN = 3

        seen_spawns = set()
        shortlist = []

        for entry in high_density:
            key = (entry["spawn"][0], entry["spawn"][1])
            if key not in seen_spawns:
                seen_spawns.add(key)
                shortlist.append(entry)

        for entry in remaining:
            if len(shortlist) >= _SHORTLIST_MAX:
                break
            key = (entry["spawn"][0], entry["spawn"][1])
            if key not in seen_spawns:
                seen_spawns.add(key)
                shortlist.append(entry)

        # ------------------------------------------------------------------
        # 4. Enforce minimum of 3 entries (relax cap if needed)
        # ------------------------------------------------------------------
        if len(shortlist) < _SHORTLIST_MIN:
            for entry in remaining:
                if len(shortlist) >= _SHORTLIST_MIN:
                    break
                key = (entry["spawn"][0], entry["spawn"][1])
                if key not in seen_spawns:
                    seen_spawns.add(key)
                    shortlist.append(entry)

        return shortlist

    # ------------------------------------------------------------------
    # Frame simulation
    # ------------------------------------------------------------------

    def _simulate_frames(self, game_state, path, unit_count, unit_hp,
                         unit_damage, unit_type):
        """Simulate a group of identical mobile units walking *path* under fire.

        The simulation advances one game frame per iteration.  Each frame:

        1. Every living unit moves one tile forward along *path*
           (``path_index`` is incremented).
        2. Units whose ``path_index`` equals the last index of *path* have
           reached the enemy edge and are recorded as edge breaches, then
           removed from the living-unit list before damage is applied.
        3. For each unique tile still occupied by living units:
           a. Friendly support shielding is applied (scout turns only).
           b. Each unit fires at the nearest non-destroyed enemy structure in
              its attack range, with ties broken by lowest y then lowest x.
              All units on the same tile fire at the same target; their total
              damage is applied to the snapshot and the structure is marked
              ``"destroyed"`` if its HP reaches 0.
        4. Turret damage is applied to units occupying each tile using a
           **furthest-along-path-first** priority.
        5. Units whose ``current_hp`` drops to zero or below are removed.
        6. ``living_unit_count`` and ``total_remaining_hp`` are recorded for
           the frame in the returned ``frames`` list.

        The simulation ends when either all units are dead or all surviving
        units have already breached (living list becomes empty).

        A mutable snapshot of enemy structures is built once before the loop
        and mutated during the simulation; ``game_state`` is never modified.

        Args:
            game_state:   Current ``GameState`` object (read-only).
            path:         Ordered list of ``[x, y]`` tiles from spawn to edge.
            unit_count:   Number of units in the attacking group.
            unit_hp:      Base (and starting) HP of each unit (float).
            unit_damage:  Attack damage per unit per frame (float).
            unit_type:    Integer unit-type constant (e.g. 3 = scout,
                          4 = demolisher).

        Returns:
            A dict::

                {
                    "edge_breach_count":    int,   # units that exited alive
                    "structure_value_removed": float,  # persistence-weighted HP
                }
        """
        if not path or unit_count <= 0 or unit_hp <= 0:
            return {"edge_breach_count": 0, "structure_value_removed": 0.0}

        # ------------------------------------------------------------------
        # Resolve attack range for the unit type
        # ------------------------------------------------------------------
        attack_range = _ATTACK_RANGE.get(unit_type, _DEFAULT_RANGE)
        range_sq = attack_range ** 2
        radius = int(math.ceil(attack_range))

        # ------------------------------------------------------------------
        # Resolve max_shield from gamelib unit type configuration (scout only).
        # max_shield caps the total bonus HP a scout unit can accumulate from
        # friendly support structures along its path.
        # ------------------------------------------------------------------
        if unit_type == _SCOUT:
            try:
                unit_info = game_state.config["unitInformation"][_SUPPORT]
                max_shield = float(unit_info.get("shieldPerUnit", _DEFAULT_SUPPORT_SHIELD))
            except Exception:
                # Fallback to known Terminal SDK constant (gamelib/unit.py shieldPerUnit)
                max_shield = _DEFAULT_SUPPORT_SHIELD
        else:
            max_shield = 0.0  # Unused for demolisher turns

        # ------------------------------------------------------------------
        # Build a mutable snapshot of all enemy (player 1) stationary units.
        # Keys are (x, y) tuples; values track current HP, unit type, and
        # whether the structure has been destroyed.  The original game_state
        # map is never written to.
        # ------------------------------------------------------------------
        struct_snapshot = {}
        for sx in range(_BOARD_MIN, _BOARD_MAX + 1):
            for sy in range(_BOARD_MIN, _BOARD_MAX + 1):
                try:
                    units_at = game_state.game_map[sx, sy]
                except Exception:
                    continue
                if not units_at:
                    continue
                for u in units_at:
                    if u.stationary and getattr(u, "player_index", -1) == 1:
                        struct_snapshot[(sx, sy)] = {
                            "hp":         float(u.health),
                            "initial_hp": float(u.health),
                            "type":       u.unit_type,
                            "destroyed":  False,
                        }

        path_len = len(path)
        last_idx = path_len - 1

        # ------------------------------------------------------------------
        # Initialise units at path_index = -1 so that the first advance
        # brings them to index 0 (the spawn tile).
        # ------------------------------------------------------------------
        living = [
            {
                "base_hp":    float(unit_hp),
                "current_hp": float(unit_hp),
                "path_index": -1,
            }
            for _ in range(unit_count)
        ]

        edge_breach_count = 0
        frames = []

        while living:
            # ---------------------------------------------------------------
            # Step 1 — advance every living unit one tile
            # ---------------------------------------------------------------
            for unit in living:
                unit["path_index"] += 1

            # ---------------------------------------------------------------
            # Step 2 — tally & remove units that reached the final tile
            # ---------------------------------------------------------------
            still_on_path = []
            for unit in living:
                if unit["path_index"] >= last_idx:
                    edge_breach_count += 1
                else:
                    still_on_path.append(unit)
            living = still_on_path

            if not living:
                break

            # ---------------------------------------------------------------
            # Step 3 — collect unique tiles occupied by living units
            # ---------------------------------------------------------------
            # Group units by their current tile, sorted so the furthest-along
            # unit within each tile appears first (path_index descending).
            tile_groups: dict = {}
            for unit in living:
                pidx = unit["path_index"]
                if pidx not in tile_groups:
                    tile_groups[pidx] = []
                tile_groups[pidx].append(unit)

            # ---------------------------------------------------------------
            # Step 3b — friendly support shielding (scout turns only)
            #
            # For each occupied tile, check whether a friendly support
            # structure is present.  If so, augment every unit on that tile
            # by the support's shield value, capped at base_hp + max_shield
            # to prevent unbounded stacking across multiple supports.
            # This step is a strict no-op on demolisher turns.
            # ---------------------------------------------------------------
            if unit_type == _SCOUT:
                for pidx, units_on_tile in tile_groups.items():
                    tile = path[pidx]
                    try:
                        support = game_state.contains_stationary_unit(tile)
                    except Exception:
                        support = None
                    if (support is not None
                            and getattr(support, "player_index", -1) == 0
                            and getattr(support, "unit_type", -1) == _SUPPORT):
                        shield_amount = float(
                            getattr(support, "shieldPerUnit", _DEFAULT_SUPPORT_SHIELD)
                        )
                        cap = unit_hp + max_shield
                        for unit in units_on_tile:
                            unit["current_hp"] = min(cap, unit["current_hp"] + shield_amount)

            # ---------------------------------------------------------------
            # Step 3c — unit attacks on enemy structures
            #
            # Every living unit fires once per frame at the nearest
            # non-destroyed enemy structure within its attack range.
            # Targeting priority:
            #   1. Nearest (smallest Euclidean distance)
            #   2. Tie-break: lowest y (furthest into our half)
            #   3. Remaining ties: lowest x (arbitrary but consistent)
            #
            # All units on the same tile share the same targeting outcome and
            # collectively apply count * unit_damage to the chosen structure.
            # If this brings the structure's HP to 0, it is marked destroyed
            # and excluded from all subsequent frames.
            # ---------------------------------------------------------------
            for pidx, units_on_tile in tile_groups.items():
                tile = path[pidx]
                tx, ty = int(tile[0]), int(tile[1])

                # Enumerate candidate structures in the bounding box
                x_lo = max(_BOARD_MIN, tx - radius)
                x_hi = min(_BOARD_MAX, tx + radius)
                y_lo = max(_BOARD_MIN, ty - radius)
                y_hi = min(_BOARD_MAX, ty + radius)

                candidates = []
                for sx in range(x_lo, x_hi + 1):
                    for sy in range(y_lo, y_hi + 1):
                        key = (sx, sy)
                        entry = struct_snapshot.get(key)
                        if entry is None or entry["destroyed"]:
                            continue
                        dist_sq = (sx - tx) ** 2 + (sy - ty) ** 2
                        if dist_sq > range_sq:
                            continue
                        # Sort key: (dist_sq, y asc, x asc)
                        candidates.append((dist_sq, sy, sx, key))

                if not candidates:
                    continue

                # Select the highest-priority target
                candidates.sort()
                target_key = candidates[0][3]

                # Apply collective damage from all units on this tile
                total_attack = len(units_on_tile) * float(unit_damage)
                target = struct_snapshot[target_key]
                target["hp"] -= total_attack
                if target["hp"] <= 0.0:
                    target["hp"] = 0.0
                    target["destroyed"] = True

            # ---------------------------------------------------------------
            # Step 4 — apply turret damage tile by tile, furthest-first
            # ---------------------------------------------------------------
            for pidx, units_on_tile in tile_groups.items():
                tile = path[pidx]

                try:
                    attackers = game_state.get_attackers(tile, 0)
                except Exception:
                    attackers = []

                if not attackers:
                    continue

                # Sum damage from all turrets targeting this tile
                tile_damage = sum(
                    getattr(a, "damage_i", 0) or getattr(a, "damage", _TURRET_DAMAGE)
                    for a in attackers
                )

                if tile_damage <= 0.0:
                    continue

                # Furthest-along first: sort by path_index descending.
                # Within the same tile all units share the same path_index,
                # so insertion order provides a stable secondary ordering.
                units_on_tile.sort(key=lambda u: -u["path_index"])

                remaining_damage = tile_damage
                for unit in units_on_tile:
                    if remaining_damage <= 0.0:
                        break
                    if unit["current_hp"] <= remaining_damage:
                        remaining_damage -= unit["current_hp"]
                        unit["current_hp"] = 0.0
                    else:
                        unit["current_hp"] -= remaining_damage
                        remaining_damage = 0.0

            # ---------------------------------------------------------------
            # Step 5 — remove dead units
            # ---------------------------------------------------------------
            living = [u for u in living if u["current_hp"] > 0.0]

            # ---------------------------------------------------------------
            # Step 6 — record frame state
            # ---------------------------------------------------------------
            living_unit_count = len(living)
            total_remaining_hp = sum(u["current_hp"] for u in living)
            frames.append({
                "living_unit_count": living_unit_count,
                "total_remaining_hp": total_remaining_hp,
            })

        # ------------------------------------------------------------------
        # Compute structure_value_removed: sum of persistence-weighted HP
        # removed from every enemy structure that took damage during the sim.
        # ------------------------------------------------------------------
        structure_value_removed = 0.0
        for entry in struct_snapshot.values():
            hp_removed = entry["initial_hp"] - entry["hp"]
            if hp_removed > 0.0:
                weight = _PERSISTENCE.get(entry["type"], 1)
                structure_value_removed += weight * hp_removed

        return {
            "edge_breach_count":       edge_breach_count,
            "structure_value_removed": structure_value_removed,
        }

    # ------------------------------------------------------------------
    # Composite scorer
    # ------------------------------------------------------------------

    def _select_best_spawn(self, candidates, state_memory, is_demolisher_turn):
        """Select the best spawn location from frame-simulation candidate results.

        Computes a composite score for each candidate and returns the winner.

        Scoring formulas:
        - **Scout turns**:
            ``score = edge_breach_count + current_lambda × structure_value_removed``
        - **Demolisher turns** (``is_demolisher_turn=True``):
            ``score = structure_value_removed``
            (edge-breach weight is set to 0 — demolishers optimise for
            structure destruction, not breaching the opponent's edge.)

        ``current_lambda`` is read from *state_memory* at call time so that
        the auto-adjustment loop's most recent update is always reflected.

        Args:
            candidates:         List of dicts produced by ``_simulate_frames``,
                                each containing:
                                - ``"spawn"``                ([x, y])
                                - ``"edge_breach_count"``   (int)
                                - ``"structure_value_removed"`` (float)
            state_memory:       ``StateMemory`` instance; ``current_lambda``
                                is read from it immediately before scoring.
            is_demolisher_turn: ``True`` when the attacking units are
                                demolishers; triggers the alternative formula.

        Returns:
            Tuple ``(best_spawn, best_score, frame_sim_prediction)``:
            - ``best_spawn`` ([x, y] or ``None`` if *candidates* is empty)
            - ``best_score`` (float; composite score of the winner, or 0.0)
            - ``frame_sim_prediction`` (int; raw ``edge_breach_count`` of the
              winning candidate — used by the lambda auto-adjustment loop to
              compare predicted vs actual breaches.  Always 0 when the list
              is empty.)
        """
        if not candidates:
            return None, 0.0, 0

        # Read lambda live — must not be cached earlier in the turn so that
        # any mid-turn update to state_memory.current_lambda is reflected.
        current_lambda = float(getattr(state_memory, "current_lambda", 0.4))

        best_spawn = None
        best_score = float("-inf")
        frame_sim_prediction = 0

        for candidate in candidates:
            edge_breach_count    = int(candidate["edge_breach_count"])
            structure_value      = float(candidate["structure_value_removed"])

            if is_demolisher_turn:
                # Demolisher turns: rank purely on structure destruction value;
                # edge-breach count is not a meaningful signal for these units.
                score = structure_value
            else:
                # Scout turns: composite of breach count and structure damage,
                # balanced by current_lambda (default 0.4, range [0.15, 0.70]).
                score = edge_breach_count + current_lambda * structure_value

            if score > best_score:
                best_score           = score
                best_spawn           = candidate["spawn"]
                frame_sim_prediction = edge_breach_count

        return best_spawn, best_score, frame_sim_prediction
