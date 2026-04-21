import collections

REQUIRED_OUTCOME_KEYS = {'lambda_used', 'edge_breaches', 'structure_value_destroyed', 'frame_sim_prediction'}

class StateMemory:
    def __init__(self):
        self.enemy_mp_history = []
        self.breach_locations = {}
        self.enemy_attack_side = 'both'
        self.our_attack_results = []
        self.turn_damage_taken = 0
        self.current_lambda = 0.4
        self.last_breach_path = []
        self.last_turn_was_demolisher_push = False
        self.demolisher_target_tiles = []
        self.outcome_buffer = collections.deque(maxlen=8)
        self.last_weak_side_returned = None

    def update(self, game_state):
        # Reset per-turn damage accumulator
        self.turn_damage_taken = 0

        # Track enemy MP over time
        enemy_mp = game_state.get_resource(game_state.MP, 1)
        self.enemy_mp_history.append(enemy_mp)

        # Recompute which side the enemy tends to attack from
        if not self.breach_locations:
            self.enemy_attack_side = 'both'
        else:
            left_count = sum(
                count for (x, _), count in self.breach_locations.items() if x < 14
            )
            right_count = sum(
                count for (x, _), count in self.breach_locations.items() if x >= 14
            )
            if left_count >= 2 * right_count:
                self.enemy_attack_side = 'left'
            elif right_count >= 2 * left_count:
                self.enemy_attack_side = 'right'
            else:
                self.enemy_attack_side = 'both'

    def record_action_frame(self, game_state):
        # Collect all bottom-edge scoring coordinates (enemy breaches our side here)
        edge_coords = set(
            map(tuple, (
                game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
                + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
            ))
        )

        for location in game_state.game_map:
            for unit in game_state.game_map[location]:
                # Only consider enemy mobile units
                if unit.player_index != 1 or unit.stationary:
                    continue

                coord = (unit.x, unit.y)
                if coord not in edge_coords:
                    continue

                # Breach detected at this coordinate
                self.breach_locations[coord] = self.breach_locations.get(coord, 0) + 1
                self.turn_damage_taken += unit.health

                # Approximate the breach path from the unit's current position
                path = game_state.find_path_to_edge([unit.x, unit.y])
                if path:
                    self.last_breach_path = path

    def set_demolisher_push(self, tiles):
        if not tiles:
            print("WARNING: set_demolisher_push called with empty tiles list; flag not set.")
            return
        self.last_turn_was_demolisher_push = True
        self.demolisher_target_tiles = tiles

    def clear_demolisher_push(self):
        self.last_turn_was_demolisher_push = False
        self.demolisher_target_tiles = []

    def record_attack_outcome(self, entry):
        missing = REQUIRED_OUTCOME_KEYS - set(entry.keys())
        if missing:
            print("WARNING: record_attack_outcome called with missing keys: {}; entry not recorded.".format(missing))
            return
        self.outcome_buffer.append(entry)

    def get_outcome_buffer(self):
        return list(self.outcome_buffer)
