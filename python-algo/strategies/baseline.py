"""
baseline.py — Balanced heuristic agent (aggression = 0.5).

Uses the middle of the aggression range so that all knobs sit at
their interpolated midpoints.  This is the "control" agent for
experiment comparisons.
"""

from .base_strategy import BaseStrategy


class BaselineStrategy(BaseStrategy):
    """Balanced agent — aggression 0.5."""

    def __init__(self):
        super().__init__(aggression=0.5)
