from enum import Enum
import copy
from .util.operations import Operation
from simulator import SimulationResults, Simulator
from gamelib.game_state import SCOUT, WALL, GameState
import gamelib
import math
from util.operations import OperationType, Operation, SpawnOperation, RemoveOperation
from abc import ABC, abstractmethod
from def_strategy import DefStrategy

class AttackDirection(Enum):
    LEFT = 'left', # spawns on right, moves left to attack
    RIGHT = 'right',

class BaseAtkStrategy(ABC):
    LEFT_BLOCKADE = [7, 7]
    RIGHT_BLOCKADE = [20, 7]
    NUM_MOBILE_PER_TURN = 5

    def __init__(self, game_state, num_mobile = 0,):
        self.game_state: GameState = game_state
        self.simulator = Simulator(game_state)
        self.num_scouts, self.num_demolishers, self.num_interceptors = self.allocate_mobile_units(num_mobile)

    ''' Methods to be overwritten '''
    @abstractmethod
    def allocate_mobile_units(self, num_mobile) -> (int, int, int):
        return (0, 0, 0)

    """
    Generates a list of operations (spawn, remove and upgrade) that attack strategy will run through.
    Both simulator and 
    """
    @abstractmethod
    def generate_operations(self, dir: AttackDirection) -> list[Operation]:
        return []
    
    def remove_blockade(self, dir: AttackDirection) -> list[Operation] | None:
        match dir:
            case AttackDirection.LEFT:
                left_blockade_unit = self.game_state.contains_stationary_unit(self.LEFT_BLOCKADE)
                return [RemoveOperation(self.LEFT_BLOCKADE)] if left_blockade_unit else None
            
            case AttackDirection.RIGHT:
                right_blockade_unit = self.game_state.contains_stationary_unit(self.RIGHT_BLOCKADE)
                return [RemoveOperation(self.RIGHT_BLOCKADE)] if right_blockade_unit else None

        return None

    def is_defense(self) -> bool:
        return False
    
    # function to compute how successful an atk strategy is
    def compute_success_value(self, num_mobile):
        return 0
    
    def run_simulation(self, dir: AttackDirection) -> int:
        operations: list[list[Operation]] = self.generate_operations(dir)

        for turn in operations:
            for op in turn:
                op.simulate_operation(self.simulator)

        # send to simulator
        simulation_results: list[int] = self.simulator.run_simulator()
        success_value = SimulationResults(simulation_results).compute_success_value()

        return success_value
    
    
    # def run_strategy(self, dir: AttackDirection, bombers_ratio = 0.5):
    #     # modify game state for this strategy
    #     operations: list[Operation] = self.generate_operations(dir, bombers_ratio)

    #     for op in operations:
    #         is_successful = op.run_operation(self.game_state)
    #         if not is_successful:
    #             print(f"Warning: some operations failed for Operation: { op.op_type }")
        
    #     # return 
    

class RushAtkStrategy(BaseAtkStrategy):
    def allocate_mobile_units(self, num_mobile) -> (int, int, int):
        if (num_mobile < 0):
            return (0, 0, 0)
        
        return (num_mobile, 0, 0)
    
    def generate_operations(self, dir: AttackDirection) -> list[list[Operation]]:
        left_spawn_location = [10, 3]
        right_spawn_location = [17, 3]

        remove_blockade_ops = self.remove_blockade(dir) 

        num_scouts = self.num_scouts if remove_blockade_ops is None else self.num_scouts + self.NUM_MOBILE_PER_TURN
        
        locations = []
        match dir:
            case AttackDirection.LEFT:
                locations = [right_spawn_location for i in range(num_scouts)]

            case AttackDirection.RIGHT:
                locations = [left_spawn_location for i in range(num_scouts)]
        
        spawn_ops = [
            SpawnOperation(SCOUT, locations)
        ]

        ops = [remove_blockade_ops, spawn_ops] if remove_blockade_ops is None else [spawn_ops]
        
        return ops

class BombRushAtkStrategy(BaseAtkStrategy):
    def allocate_mobile_units(self, num_mobile) -> (int, int, int):
        if (num_mobile < 0): 
            return (0, 0, 0)

        return (num_mobile, 0, 0)
    
    def generate_operations(self, dir: AttackDirection, bombers_ratio = 0.5) -> list[list[Operation]]:
        left_bomber_spawn_location = [8, 5]
        left_scout_spawn_location = [7, 6]

        right_bomber_spawn_location = [19, 5]
        right_scout_spawn_location = [20, 6]

        remove_blockade_ops = self.remove_blockade(dir) 

        num_scouts = self.num_scouts if remove_blockade_ops is None else self.num_scouts + self.NUM_MOBILE_PER_TURN

        num_left_bombers = 0
        num_left_scouts = 0

        num_right_bombers = 0
        num_right_scouts = 0

        match dir:
            case AttackDirection.LEFT:
                num_right_bombers = math.floor(bombers_ratio * num_scouts)
                num_right_scouts = num_scouts - num_right_bombers

            case AttackDirection.RIGHT:
                num_left_bombers = math.floor(bombers_ratio * num_scouts)
                num_left_scouts = num_scouts - num_left_bombers

        bomber_locations = [left_bomber_spawn_location for i in range(num_left_bombers)].extend([right_bomber_spawn_location for i  in range(num_right_bombers)])
        scout_locations = [left_scout_spawn_location for i in range(num_left_scouts)].extend([right_scout_spawn_location for i  in range(num_right_scouts)])

        spawn_ops = [
            SpawnOperation(SCOUT, bomber_locations), 
            SpawnOperation(SCOUT, scout_locations)
        ]

        ops = [remove_blockade_ops, spawn_ops] if remove_blockade_ops is None else [spawn_ops]
        
        return ops
    
class CannonAtkStrategy(BaseAtkStrategy):
    def allocate_mobile_units(self, num_mobile) -> (int, int, int):
        if (num_mobile < 0): 
            return (0, 0, 0)

        return (num_mobile, 0, 0)

    def generate_operations(self, dir: AttackDirection, bombers_ratio = 0.5) -> list[list[Operation]]:

        # Removal Operations -- Turn 1
        left_wall_removal = [1, 12]
        right_wall_removal = [26, 12]

        removal_ops = []

        match dir:
            case AttackDirection.LEFT:
                removal_ops.append(RemoveOperation(right_wall_removal))

            case AttackDirection.RIGHT:
                removal_ops.append(RemoveOperation(left_wall_removal))

        remove_blockade_ops = self.remove_blockade(dir)
        removal_ops.extend(remove_blockade_ops)

        num_scouts = self.num_scouts if len(removal_ops) == 0 else self.num_scouts + self.NUM_MOBILE_PER_TURN

        # Spawn Operations -- Turn 2 (Same as BombRush)
        left_bomber_spawn_location = [8, 5]
        left_scout_spawn_location = [7, 6]

        right_bomber_spawn_location = [19, 5]
        right_scout_spawn_location = [20, 6]

        left_walls_to_spawn = [[2, 13], [3, 13], [4, 12]]
        right_walls_to_spawn = [[24, 13], [25, 13], [23, 12]]

        num_left_bombers = 0
        num_left_scouts = 0

        num_right_bombers = 0
        num_right_scouts = 0

        match dir:
            case AttackDirection.LEFT:
                num_right_bombers = math.floor(bombers_ratio * num_scouts)
                num_right_scouts = num_scouts - num_right_bombers

            case AttackDirection.RIGHT:
                num_left_bombers = math.floor(bombers_ratio * num_scouts)
                num_left_scouts = num_scouts - num_left_bombers

        bomber_locations = [left_bomber_spawn_location for i in range(num_left_bombers)].extend([right_bomber_spawn_location for i  in range(num_right_bombers)])
        scout_locations = [left_scout_spawn_location for i in range(num_left_scouts)].extend([right_scout_spawn_location for i  in range(num_right_scouts)])

        bomb_rush_ops = [
            # spawn walls
            SpawnOperation(WALL, right_walls_to_spawn),
            SpawnOperation(WALL, left_walls_to_spawn),

            # spawn scouts
            SpawnOperation(SCOUT, bomber_locations), 
            SpawnOperation(SCOUT, scout_locations)
        ]

        ### 
        
        return [removal_ops, bomb_rush_ops]


class AttackStrategyNames(Enum):
    RUSH = 'rush',
    BOMB_RUSH = 'bomb_rush',
    CANNON = 'cannon'

all_attack_strategy_names = [atk.name for atk in AttackStrategyNames]

def find_best_strategy(game_state, num_mobile, strategies: list[AttackStrategyNames] = all_attack_strategy_names) -> tuple[list[Operation], AttackStrategyNames, AttackDirection]:

    best_strategy_success_value = None
    best_strategy_ops = None
    best_strategy_name = None
    best_strategy_dir = None

    for s in strategies:
        match s:
            case AttackStrategyNames.RUSH:
                strat = RushAtkStrategy(game_state, num_mobile)

                best_rush_strat = None
                best_dir = None
                max_success_value = None

                for d in AttackDirection:
                    success_value = strat.run_simulation(d)
                    if max_success_value is None or max_success_value < success_value:
                        best_rush_strat = strat.generate_operations(d)
                        best_dir = d
                        max_success_value = success_value
                
                if best_strategy_success_value is None or best_strategy_success_value < max_success_value:
                    best_strategy_ops = best_rush_strat
                    best_strategy_name = s
                    best_strategy_dir = best_dir
                    best_strategy_success_value = max_success_value
            
            case AttackStrategyNames.BOMB_RUSH:
                strat = BombRushAtkStrategy(game_state, num_mobile)

                best_bomb_rush_strat = None
                best_dir = None
                max_success_value = None

                for d in AttackDirection:
                    success_value = strat.run_simulation(dir)
                    if max_success_value is None or max_success_value < success_value:
                        best_bomb_rush_strat = strat.generate_operations(d)
                        best_dir = d
                        max_success_value = success_value
                
                if best_strategy_success_value is None or best_strategy_success_value < max_success_value:
                    best_strategy_ops = best_bomb_rush_strat
                    best_strategy_name = s
                    best_strategy_dir = best_dir
                    best_strategy_success_value = max_success_value
            
            case AttackStrategyNames.CANNON:
                strat = CannonAtkStrategy(game_state, num_mobile)

                best_cannon_strat = None
                best_dir = None
                max_success_value = None

                for d in AttackDirection:
                    success_value = strat.run_simulation(dir)
                    if max_success_value is None or max_success_value < success_value:
                        best_cannon_strat = strat.generate_operations(d)
                        best_dir = d
                        max_success_value = success_value
                
                if best_strategy_success_value is None or best_strategy_success_value < max_success_value:
                    best_strategy_ops = best_cannon_strat
                    best_strategy_name = s
                    best_strategy_dir = best_dir
                    best_strategy_success_value = max_success_value

    
    # if best_strategy_success_value is None or best_strategy_success_value < threshold: use Defense Strategy
    if best_strategy_ops is None or best_strategy_success_value < 0.6: # THRESHOLD
        best_strategy_ops = DefStrategy(game_state).generate_operations()
        best_strategy_name = None
        best_strategy_dir = None

    return (best_strategy_ops, best_strategy_name, best_strategy_dir)
