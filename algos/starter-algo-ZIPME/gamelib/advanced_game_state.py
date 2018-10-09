from .game_state import GameState, GameUnit
import sys
import warnings

class AdvancedGameState(GameState):
    """A version of gamestate with access to a few more advanced functions

    """
    def get_target(self, attacking_unit):
        """Returns target of given unit based on current map of the game board. 
        A Unit can often have many other units in range, and Units that attack do so once each frame.

        Their targeting priority is as follows:
            Infantry > Nearest Unit > Lowest Stability > Lowest Y position > Closest to edge (Highest distance of X from the boards center, 13.5)

        Args:
            * attacking_unit: A GameUnit

        Returns:
            The GameUnit this unit would choose to attack.

        """
        
        from .game_state import SCRAMBLER, is_stationary

        if not isinstance(attacking_unit, GameUnit):
            warnings.warn("Passed a {} to get_target as attacking_unit. Expected a GameUnit.".format(type(attacking_unit)))
            return

        attacker_location = [attacking_unit.x, attacking_unit.y]
        possible_locations = self.game_map.get_locations_in_range(attacker_location, attacking_unit.range)
        target = None
        target_stationary = True
        target_distance = sys.maxsize
        target_stability = sys.maxsize
        target_y = self.ARENA_SIZE
        target_x_distance = 0

        for location in possible_locations:
            for unit in self.game_map[location]:
                """
                NOTE: scrambler units cannot attack firewalls so skip them if unit is firewall
                """
                if unit.player_index == attacking_unit.player_index or (attacking_unit.unit_type == SCRAMBLER and is_stationary(unit)):
                    continue

                new_target = False
                unit_stationary = unit.stationary
                unit_distance = self.game_map.distance_between_locations(location, [attacking_unit.x, attacking_unit.y])
                unit_stability = unit.stability
                unit_y = unit.y
                unit_x_distance = abs(self.HALF_ARENA - 0.5 - unit.x)

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

    def get_attackers(self, location, player_index):
        """Gets the destructors threatening a given location

        Args:
            * location: The location of a hypothetical defender
            * player_index: The index corresponding to the defending player, 0 for you 1 for the enemy

        Returns:
            A list of destructors that would attack a unit controlled by the given player at the given location

        """
        
        from .game_state import DESTRUCTOR, UNIT_TYPE_TO_INDEX

        if not player_index == 0 and not player_index == 1:
            self._invalid_player_index(player_index)
        if not self.game_map.in_arena_bounds(location):
            warnings.warn("Location {} is not in the arena bounds.".format(location))

        attackers = []
        """
        Get locations in the range of DESTRUCTOR units
        """
        possible_locations= self.game_map.get_locations_in_range(location, self.config["unitInformation"][UNIT_TYPE_TO_INDEX[DESTRUCTOR]]["range"])
        for location in possible_locations:
            for unit in self.game_map[location]:
                if unit.unit_type == DESTRUCTOR and unit.player_index != player_index:
                    attackers.append(unit)
        return attackers
