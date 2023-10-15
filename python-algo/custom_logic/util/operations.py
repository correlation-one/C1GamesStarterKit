from enum import Enum 
from simulator import Simulator
from gamelib.game_state import GameState
from abc import ABC, abstractmethod

class OperationType(Enum):
    SPAWN = 'spawn',
    REMOVE = 'remove',
    UPGRADE = 'upgrade',


class Operation(ABC):
    def __init__(self, op_type: OperationType):
        self.op_type = op_type

    @abstractmethod
    def simulate_operation(self, simulator: Simulator):
        pass

    @abstractmethod
    def run_operation(self, game_state) -> int:
        return False

    def run_simulator(self):
        return self.simulate_operation()

    """
    returns: if all operations are successful
    E.g., all units successfully spawned, all unit at locations successfully upgraded, etc.
    """
    def run_strategy(self) -> bool:
        return self.run_operation()


class SpawnOperation(Operation):
    def __init__(self, unit_type: str, locations: list[int] | list[list[int]]):
        super().__init__(OperationType.SPAWN)
        self.unit_type = unit_type
        self.locations = locations
    
    def simulate_operation(self, simulator: Simulator):
        simulator.simulate_spawn(self.unit_type, self.locations)
    
    def run_operation(self, game_state: GameState) -> int:
        return game_state.attempt_spawn(self.unit_type, self.locations)

class RemoveOperation(Operation):
    def __init__(self, locations: list[int] | list[list[int]]):
        super().__init__(OperationType.REMOVE)
        self.locations = locations
    
    def simulate_operation(self, simulator: Simulator):
        simulator.simulate_remove(self.locations)
    
    def run_operation(self, game_state: GameState) -> int:
        return game_state.attempt_remove(self.locations)

class UpgradeOperation(Operation):
    def __init__(self, locations: list[int] | list[list[int]]):
        super().__init__(OperationType.UPGRADE)
        self.locations = locations
    
    def simulate_operation(self, simulator: Simulator):
        simulator.simulate_upgrade(self.locations)
    
    def run_operation(self, game_state: GameState) -> int:
        return game_state.attempt_upgrade(self.locations)
