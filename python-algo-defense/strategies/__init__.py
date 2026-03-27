from .baseline import BaselineStrategy
from .offense import OffenseStrategy
from .defense import DefenseStrategy

STRATEGIES = {
    "baseline": BaselineStrategy,
    "offense": OffenseStrategy,
    "defense": DefenseStrategy,
}
