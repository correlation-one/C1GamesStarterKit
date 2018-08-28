from .game import GameState
import sys

'''
These functions are a bit more advanced, and most algos are 
unlikely to need them. If you want to use them, you can 
initialize an AdvancedGameState instead of Gamestate in algo_strategy
'''

class AdvancedGameState(GameState):
    def get_target(self, attacking_unit):
        '''
        Returns target of given unit based on current map of the game board.
        '''
        from .game import SCRAMBLER, is_stationary

        # Target priority: Infantry > Nearest Unit > Lowest Stability > Lowest Y position > Closest to edge (Highest distance of X from the boards center, 13.5)
        # Note that it is rare that any condition other than the first 2 matter
        attacker_location = [attacking_unit.x, attacking_unit.y]
        possible_locations = self.map.get_locations_in_range(attacker_location, attacking_unit.range)
        target = None
        target_stationary = True
        target_distance = sys.maxint
        target_stability = sys.maxint
        target_y = self.arena_size
        target_x_distance = 0

        for location in possible_locations:
            for unit in self.map[location]:
                # Note scrambler units cannot attack firewalls so skip them if unit is firewall
                if unit.player_id == attacking_unit.player_id or (attacking_unit.unit_type == SCRAMBLER and is_stationary(unit)):
                    continue

                new_target = False
                unit_stationary = unit.stationary
                unit_distance = self.map.distance_between_locations(location, [attacking_unit.x, attacking_unit.y])
                unit_stability = unit.stability
                unit_y = unit.y
                unit_x_distance = abs(self.half_arena - 0.5 - unit.x)

                if target_stationary and not unit_stationary:
                    new_target = True
                elif not target_stationary and unit_stationary:
                    continue
                
                if target_distance > unit_distance:
                    new_target = True
                elif target_distance < unit_distance and not new_target:
                    continue

                if target_stability > unit_stability:
                    new_target = True
                elif target_stability < unit_stability and not new_target:
                    continue

                if target_y > unit_y:
                    new_target = True
                elif target_y < unit_y and not new_target:
                    continue       

                if target_x_distance < unit_x_distance:
                    new_target = True
                
                if new_target:
                    target = unit
                    target_stationary = unit_stationary
                    target_distance = unit_distance
                    target_stability = unit_stability
                    target_y = unit_y
                    target_x_distance = unit_x_distance
        return target

    def get_attackers(self, location, player_id):
        '''
        Returns list of destructors that would attack a unit at the given location with the given player id.
        '''
        from .game import DESTRUCTOR, UNIT_TYPE_TO_INDEX

        attackers = []
        #Get locations in the range of DESTRUCTOR units
        possible_locations= self.map.get_locations_in_range(location, self.config["unitInformation"][UNIT_TYPE_TO_INDEX[DESTRUCTOR]]["range"])
        for location in possible_locations:
            for unit in self.map[location]:
                if unit.unit_type == DESTRUCTOR and unit.player_id != player_id:
                    attackers.append(unit)
        return attackers
