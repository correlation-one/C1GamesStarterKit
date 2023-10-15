from gamelib.game_state import WALL, GameState
from custom_logic.util.operations import SpawnOperation, Operation


class DefStrategy:
    LEFT_BLOCKADE = [7, 7]
    RIGHT_BLOCKADE = [20, 7]

    def __init__(self, game_state: GameState):
        self.game_state: GameState = game_state

    def is_defending(self) -> bool:
        return True

    def generate_operations(self) -> list[list[Operation]]:
        build_blockade_ops = [
            SpawnOperation(WALL, [self.LEFT_BLOCKADE, self.RIGHT_BLOCKADE])
        ]
        return [build_blockade_ops]


    