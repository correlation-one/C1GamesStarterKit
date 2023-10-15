# will be implemented later
class Simulator:
    def __init__(self, game_state):
        pass

    def simulate_spawn(self, unit_type, locations: list[int] | list[list[int]], num = 1) -> int:
        pass

    def simulate_remove(self, locations: list[int] | list[list[int]]) -> int:
        pass

    def run_simulator() -> list[int]:
        pass


class SimulationResults:
    def __init__(self, results: list[float]):
        self.dmg_to_hp = results[0]
        self.dmg_to_structure = results[1]
        self.dmg_to_mobile = results[2]
        self.num_structures_destroyed = results[3]
        self.num_mobile_destroyed = results[4]

    def compute_success_value() -> int:
        return 0