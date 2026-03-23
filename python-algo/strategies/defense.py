"""
defense.py — Defense-focused agent variant (aggression = 0.15).

Low aggression means:
  • High MP threshold → only attacks when overwhelmingly resourced
  • Upgrades everything → walls and turrets are prioritized
  • Longer interceptor stall → turtles early game
  • Scout rush disabled → conserves MP for interceptors
  • All Phase 2 and Phase 3 defense locations built
  • Supports disabled → SP goes to walls/turrets instead
"""

from .base_strategy import BaseStrategy


class DefenseStrategy(BaseStrategy):
    """Turtle / fortress agent — aggression 0.15."""

    def __init__(self):
        super().__init__(aggression=0.15)
