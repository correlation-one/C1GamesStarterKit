"""
offense.py — Offense-focused agent variant (aggression = 0.85).

High aggression means:
  • Low MP threshold → attacks earlier and more often
  • Skips wall upgrades → saves SP for supports that buff mobile units
  • Short interceptor stall → gets aggressive faster
  • Extra support locations enabled
  • Fewer Phase 2/3 defense structures built
"""

from .base_strategy import BaseStrategy


class OffenseStrategy(BaseStrategy):
    """Glass-cannon agent — aggression 0.85."""

    def __init__(self):
        super().__init__(aggression=0.85)
