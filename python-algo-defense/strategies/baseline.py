"""
baseline.py — Balanced heuristic agent.

Uses the default weights from BaseStrategy with no overrides.
This is the "control" agent for experiment comparisons.
"""

from .base_strategy import BaseStrategy


class BaselineStrategy(BaseStrategy):
    """
    Balanced agent — equal priority on defense and offense.
    All weights remain at their base defaults.
    """

    # Explicitly state the defaults for clarity / documentation
    DEFENSE_SP_RATIO        = 0.6
    OFFENSE_MP_THRESHOLD    = 10
    UPGRADE_PRIORITY        = True
    SUPPORT_ENABLED         = True
    INTERCEPTOR_EARLY_TURNS = 5
    SCOUT_RUSH_ENABLED      = True
    DEMOLISHER_LINE_ENABLED = True
