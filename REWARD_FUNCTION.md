# Reward / Objective Function Documentation

## Formal Definition

The agent's implicit reward function at each turn is:

```
R(s, c) = c · offense_value(s) + (1 - c) · defense_value(s)
```

Where:
- **`c`** = `aggression` parameter (float, 0.0 → 1.0)
- **`offense_value(s)`** = value placed on spending MP (mobile points) to attack and score
- **`defense_value(s)`** = value placed on spending SP (structure points) to build and survive
- **`s`** = current game state

---

## How `c` Controls Agent Behavior

All weights are linearly interpolated using:

```python
_lerp(defense_val, offense_val, c)  →  defense_val + (offense_val - defense_val) * c
```

| Parameter | c = 0.0 (Full Defense) | c = 0.5 (Balanced) | c = 1.0 (Full Offense) |
|:---|:---:|:---:|:---:|
| MP threshold to attack | 18 | 11.5 | 5 |
| Upgrade structures? | ✅ Yes | ✅ Yes | ❌ No |
| Build supports? | ❌ No | ✅ Yes | ✅ Yes |
| Early stall turns | 8 | 5 | 2 |
| Scout rush enabled? | ❌ No | ✅ Yes | ✅ Yes |
| Defense Phase 2/3 built? | 100% | 70% | 0–40% |

---

## Concrete Interpretations at Each Level

| Aggression `c` | Behavior Label | What the Agent Does |
|:---:|:---:|:---|
| 0.0 | Turtle | Hoards SP, builds maximal defenses, barely attacks |
| 0.1 | Defensive | Strong walls, minimal offense |
| 0.2 | Passive | Neither fully turtles nor attacks effectively |
| 0.3 | Inefficient | Tries to attack but collapses under pressure |
| 0.4 | Strategic | Balanced — builds key defenses, attacks when ready |
| 0.5 | Optimal | Efficient resource use, adaptive attack timing |
| 0.6 | Aggressive | Prioritizes offense, lighter defense |
| 0.7 | Overcommitted | Heavy offense, insufficient defensive structure |
| 0.8 | Chaotic | Inconsistent attacks, minimal walls |
| 0.9 | Fragile | Near full offense, collapses quickly |
| 1.0 | Glass Cannon | Maximum offense, no defense at all |

---

## Experiment Argument

> **"We tested how changing one reward/objective parameter `c` changes agent behavior
> and outcomes in C1 Terminal."**

The same code, the same decision pipeline, the same opponent — only `c` changes.
Small shifts in `c` produce phase transitions:
- `c = 0.6` → 100% win rate
- `c = 0.7` → 0% win rate

This demonstrates **reward hacking**: the agent at `c = 1.0` maximizes destructive
offense (the proxy metric) but fails at the true goal of winning the game.

---

## Key Files

| File | Role |
|:---|:---|
| `python-algo/strategies/base_strategy.py` | All reward weights and `_lerp` logic |
| `python-algo/algo_strategy.py` | Reads `AGGRESSION` env var, initializes strategy |
| `run_sweep.py` | Runs matches across all `c` values |
| `analyze_results.py` | Parses replays → `sweep_results.csv` + `sweep_summary.csv` |
| `plot_results.py` | Generates charts from CSVs |
