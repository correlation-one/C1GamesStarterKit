# Terminal Algo Strategy — AI Alignment Experiment

**CS 3501: AI & Humanity (Spring 2026) — Professor David Evans**

> How does changing a single "aggression" parameter in an AI agent's objective function
> affect its behavior, performance, and resource allocation?

This project uses [Correlation One's C1 Terminal](https://terminal.c1games.com/) game
(a tower-defense AI competition) to experimentally study how objective functions shape
agent behavior — a concrete analogy for AI alignment.

---

## Architecture

Every agent runs the **same three-step decision pipeline** on every turn:

```
1. Evaluate the board   →  gather metrics (health, resources, enemy positions)
2. Build defenses       →  place turrets, walls, supports
3. Decide attack        →  interceptor stall, scout rush, or demolisher line
```

The only thing that changes is a single **`aggression`** parameter (float, 0.0 → 1.0):

| aggression | Style | MP Threshold | Upgrades? | Supports? | Early Stall Turns | Scout Rush? |
|:----------:|:-----:|:-----------:|:---------:|:---------:|:-----------------:|:-----------:|
| 0.0 | Full defense | 18 | ✅ | ❌ | 8 | ❌ |
| 0.5 | Balanced | 11.5 | ✅ | ✅ | 5 | ✅ |
| 1.0 | Full offense | 5 | ❌ | ✅ | 2 | ✅ |

All weights are interpolated with `_lerp(defense_val, offense_val, aggression)`.

### Key files

```
python-algo/
  algo_strategy.py          # Entry point — reads AGGRESSION env var
  strategies/
    base_strategy.py        # Core pipeline + all parameterized logic
    baseline.py             # aggression = 0.50
    offense.py              # aggression = 0.85
    defense.py              # aggression = 0.15
    __init__.py             # Registry + make_strategy() factory
  gamelib/                  # C1 Terminal SDK (unchanged)

python-algo-starter/        # Fixed opponent (unmodified starter algo)

run_sweep.py                # Parameter sweep runner
analyze_results.py          # Replay parser → CSV + summary table
sweep_results.csv           # Latest sweep output
```

---

## How to Run

### Prerequisites
- **Python 3** (any recent version)
- **Java 21+** (for the game engine)

### Quick test (no Java needed)
```bash
# Test with default balanced agent
./scripts/test_algo_mac python-algo/

# Test with a specific aggression value
AGGRESSION=0.3 ./scripts/test_algo_mac python-algo/
```

### Run a single match (requires Java)
```bash
java -jar engine.jar work python-algo/run.sh python-algo-starter/run.sh
# Replay file appears in replays/
```

### Run the full parameter sweep
```bash
# 11 evenly spaced values: 0.0, 0.1, 0.2, ... 1.0
python3 run_sweep.py

# Or customize:
python3 run_sweep.py --steps 21              # finer grain (0.00, 0.05, ..., 1.00)
python3 run_sweep.py --values 0.3 0.45 0.6   # specific values
python3 run_sweep.py --steps 11 --repeats 3   # 3 runs per value for statistical significance

# Then analyze:
python3 analyze_results.py
# → prints summary table + writes sweep_results.csv
```

---

## Results (11-value sweep, 1 run each)

| Aggression | Winner | Agent Pts | Opp Pts | Turns | SP Spent | MP Spent |
|:----------:|:------:|:---------:|:-------:|:-----:|:--------:|:--------:|
| 0.00 | ✅ agent | 6 | 5 | 100 | 464 | 950 |
| 0.10 | ✅ agent | 9 | 3 | 100 | 508 | 950 |
| 0.20 | ❌ opponent | 6 | 43 | 91 | 470 | 838 |
| 0.30 | ❌ opponent | 5 | 43 | 49 | 290 | 350 |
| **0.40** | **✅ agent** | **43** | **0** | **43** | **174** | **420** |
| **0.50** | **✅ agent** | **40** | **7** | **33** | **174** | **300** |
| **0.60** | **✅ agent** | **46** | **35** | **25** | **177** | **207** |
| 0.70 | ❌ opponent | 9 | 40 | 17 | 107 | 186 |
| 0.80 | ❌ opponent | 9 | 40 | 17 | 107 | 188 |
| 0.90 | ❌ opponent | 13 | 43 | 21 | 108 | 239 |
| 1.00 | ❌ opponent | 16 | 47 | 11 | 70 | 118 |

### Key takeaways

1. **The sweet spot is aggression 0.4–0.6.** Agents that balance offense and defense
   dominate — they score the most points, concede the fewest, and win decisively.

2. **Extremes both fail, but for different reasons:**
   - **Full defense (0.0–0.1):** Survives to turn 100 but barely scores. "Wins" only because
     the starter opponent is weak. Against a better opponent this turtling stalls out.
   - **Full offense (0.7–1.0):** Scores some points but gets overwhelmed fast (games end by turn 11–21).
     Not enough structure to survive counter-attacks.

3. **The 0.2–0.3 zone is a "valley"** — too aggressive to turtle effectively, but not aggressive
   enough to kill the opponent before defenses crumble. Worst of both worlds.

4. **Resource efficiency varies dramatically:**
   - Defense agents spend 464+ SP and 950 MP over 100 turns but score only 6–9 points.
   - Balanced agents spend ~174 SP and ~300 MP in 33 turns and score 40+ points.

### Alignment connection

This is exactly the core challenge of AI alignment: the *same decision pipeline* produces
dramatically different outcomes based on how its objective function is weighted. A
"misaligned" agent (too aggressive or too conservative) doesn't need different code — it
just has the wrong parameter. Small changes in the objective (moving from 0.6 to 0.7)
can cause a phase transition from winning to losing.

---

## 🤝 Contributing / Next Steps

Things groupmates can work on:
- **Run with `--repeats 3`** for statistical significance and update the results table
- **Try finer-grained sweep** around the sweet spot: `--values 0.35 0.40 0.45 0.50 0.55 0.60 0.65`
- **Write up the alignment analysis** for the final report — connect results to class themes
- **Add a plotting script** (matplotlib) to visualize aggression vs. win rate / points
- **Test against a stronger opponent** — modify `python-algo-starter/` with a smarter strategy

---

## Original Starter Kit

This repo is forked from the [C1GamesStarterKit](https://github.com/correlation-one/C1GamesStarterKit).
See `python-algo/README.md` and `scripts/README.md` for original C1 documentation.

#### Python Requirements

Python algos require Python 3 to run. If you are running Unix (Mac OS or Linux), the command `python3` must run on 
Bash or Terminal. If you are running Windows, the command `py -3` must run on PowerShell.
   
#### Java Requirements

Java algos require the Java Development Kit. Java algos also require [Gradle]
(https://gradle.org/install/) for compilation.
   
## Running Algos

To run your algo locally or on our servers, or to enroll your algo in a competition, please see the [documentation 
for the Terminal command line interface in the scripts directory](https://github.com/correlation-one/AIGamesStarterKit/tree/master/scripts)
