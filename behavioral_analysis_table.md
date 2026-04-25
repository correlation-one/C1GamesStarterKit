# Behavioral Analysis Table

This table highlights how the bot's behavior changes at different aggression levels. The focus is on resource allocation, survival, and observed strategies rather than win rates.

| Aggression Level | Resource Allocation (SP vs. MP) | Avg Turns Survived | Observed Behavior          |
|------------------|---------------------------------|--------------------|----------------------------|
| 0.0              | High SP, Low MP                | 100                | Turtling: prioritizes defense, rarely attacks. |
| 0.1              | High SP, Low MP                | 99                 | Defensive: builds strong walls, minimal offense. |
| 0.2              | Moderate SP, Low MP            | 93                 | Inefficient: neither fully defensive nor offensive. |
| 0.3              | Moderate SP, Moderate MP       | 59                 | Overextended: attempts offense but lacks defense. |
| 0.4              | Balanced SP and MP             | 44                 | Strategic: adapts to opponent, balances offense and defense. |
| 0.5              | Balanced SP and MP             | 34                 | Optimal: efficient resource use, strategic attacks. |
| 0.6              | Low SP, High MP                | 25                 | Aggressive: prioritizes offense, minimal defense. |
| 0.7              | Low SP, High MP                | 16                 | Overcommitted: heavy offense, collapses quickly. |
| 0.8              | Low SP, High MP                | 17                 | Chaotic: neglects defense, inconsistent attacks. |
| 0.9              | Low SP, High MP                | 16                 | Fragile: focuses on destruction, ignores survival. |
| 1.0              | Low SP, High MP                | 11                 | Glass Cannon: maximizes offense, no defense. |

---

## Observations
- **Balanced Strategies (0.4–0.5):**
  - These levels achieve the best balance between offense and defense, leading to efficient resource use and strategic wins.
- **Defensive Extremes (0.0–0.1):**
  - These levels prioritize survival but fail to capitalize on offensive opportunities.
- **Offensive Extremes (0.7–1.0):**
  - These levels overcommit to offense, leading to quick collapses due to lack of defense.
- **Middle Ground (0.2–0.3):**
  - These levels struggle to find a clear strategy, resulting in inefficient behavior.

---

## Suggested Use
- Pair this table with qualitative descriptions or replays to illustrate the observed behaviors.
- Use the heatmap to show transitions in behavior, not just win rates.
- Highlight how small changes in the aggression parameter lead to significant shifts in strategy and outcomes.