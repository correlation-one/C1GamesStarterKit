class ThreatAnalyzer:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Private classifiers
    # ------------------------------------------------------------------

    def _classify_scout_rush(self, state_memory):
        """Return True when enemy MP has increased for 3+ consecutive turns
        with no observed spend (all deltas positive)."""
        history = state_memory.enemy_mp_history
        if len(history) < 4:
            return False
        last_four = history[-4:]
        deltas = [last_four[i + 1] - last_four[i] for i in range(3)]
        return all(d > 0 for d in deltas)

    def _classify_demolisher_line(self, game_state):
        """Return True when a contiguous horizontal wall segment of 5+ tiles
        exists on absolute rows 13 or 14 (enemy half border rows)."""
        wall_type = game_state.config["unitInformation"][0]["shorthand"]
        for row in (13, 14):
            run = 0
            for x in range(28):
                units = game_state.game_map[x, row]
                is_wall = any(
                    u.unit_type == wall_type and u.player_index == 1
                    for u in units
                )
                if is_wall:
                    run += 1
                    if run >= 5:
                        return True
                else:
                    run = 0
        return False

    def _classify_interceptor_wall(self, game_state):
        """Return True when the enemy has interceptors on rows 14 or 15
        (the lowest rows of the enemy's territory)."""
        interceptor_type = game_state.config["unitInformation"][5]["shorthand"]
        for row in (14, 15):
            for x in range(28):
                units = game_state.game_map[x, row]
                if any(u.unit_type == interceptor_type and u.player_index == 1
                       for u in units):
                    return True
        return False

    def _score_weak_side(self, game_state, state_memory):
        """Evaluate both halves of the enemy board by summing turret health
        ratios, then return (weak_side, weak_side_score).

        Columns 0-13  = 'left'
        Columns 14-27 = 'right'
        Enemy rows = 14-27  (player_index == 1)

        If both sums are within 10% of each other, alternate using
        state_memory.last_weak_side_returned to avoid predictability.
        """
        turret_type = game_state.config["unitInformation"][2]["shorthand"]

        left_score = 0.0
        right_score = 0.0

        for y in range(14, 28):
            for x in range(28):
                units = game_state.game_map[x, y]
                for u in units:
                    if u.unit_type != turret_type or u.player_index != 1:
                        continue
                    ratio = u.health / u.max_health
                    if x < 14:
                        left_score += ratio
                    else:
                        right_score += ratio

        # Determine which side is weaker
        max_score = max(left_score, right_score)

        if max_score == 0.0:
            # No turrets on either side — alternate to avoid repetition
            near_equal = True
        else:
            near_equal = abs(left_score - right_score) / max_score < 0.10

        if near_equal:
            last = getattr(state_memory, 'last_weak_side_returned', None)
            if last == 'left':
                chosen = 'right'
            else:
                chosen = 'left'
        else:
            chosen = 'left' if left_score <= right_score else 'right'

        if state_memory is not None:
            state_memory.last_weak_side_returned = chosen

        score = left_score if chosen == 'left' else right_score
        return chosen, score

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def assess(self, game_state, state_memory=None):
        try:
            scout_rush = (
                state_memory is not None
                and self._classify_scout_rush(state_memory)
            )
            demolisher_line = self._classify_demolisher_line(game_state)
            interceptor_wall = self._classify_interceptor_wall(game_state)

            if scout_rush:
                enemy_strategy = 'scout_rush'
            elif demolisher_line:
                enemy_strategy = 'demolisher_line'
            elif interceptor_wall:
                enemy_strategy = 'interceptor_wall'
            else:
                enemy_strategy = 'unknown'

            push_imminent = scout_rush or demolisher_line or interceptor_wall

            weak_side, weak_side_score = self._score_weak_side(game_state, state_memory)
        except Exception:
            enemy_strategy = 'unknown'
            push_imminent = False
            weak_side = 'left'
            weak_side_score = 0.0

        return {
            'enemy_strategy': enemy_strategy,
            'push_imminent': push_imminent,
            'weak_side': weak_side,
            'weak_side_score': weak_side_score,
        }
