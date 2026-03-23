from .base_strategy import BaseStrategy
from .baseline import BaselineStrategy
from .offense import OffenseStrategy
from .defense import DefenseStrategy

STRATEGIES = {
    "baseline": BaselineStrategy,
    "offense": OffenseStrategy,
    "defense": DefenseStrategy,
}

# Named-preset aggression values (for reference / convenience)
PRESETS = {
    "defense":  0.15,
    "baseline": 0.50,
    "offense":  0.85,
}


def make_strategy(aggression: float) -> BaseStrategy:
    """Create an agent with an arbitrary aggression value (0.0 – 1.0)."""
    return BaseStrategy(aggression=aggression)
