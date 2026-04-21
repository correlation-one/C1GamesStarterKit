# Starter Algo

## File Overview

```
starter-algo
 │
 ├──gamelib
 │   ├──__init__.py# Custom Algo — Design Reference

This document explains the architecture and key design decisions for the
custom algo strategy implemented in this directory.  It is intended as a
reviewer/contributor guide; for SDK-level documentation of the `gamelib`
package see `documentation/`.

---

## File Overview

```
python-algo/
 │
 ├── gamelib/               # Unmodified Terminal SDK helpers
 │
 ├── algo_strategy.py       # Entry point — wires all modules together
 ├── state_memory.py        # Cross-turn persistent state
 ├── threat_analyzer.py     # Enemy strategy classification
 ├── economy_controller.py  # SP build queue + attack gating
 ├── defense_manager.py     # Structure placement and repair
 ├── attack_planner.py      # Spawn scoring, sim, and lambda tuning
 │
 ├── documentation/         # Sphinx source for gamelib API docs
 ├── README.md              # This file
 ├── run.sh / run.ps1       # Engine launch scripts (do not modify)
 └── algo.json              # Algo metadata
```

---

## Turn pipeline

Each turn `AlgoStrategy.on_turn()` runs the following stages in order:

```
StateMemory.update()
    └─ enemy MP history, breach-side classification

ThreatAnalyzer.assess()
    └─ enemy strategy tag, push-imminent flag, weak-side score

EconomyController.decide()
    └─ attack_this_turn bool, ordered SP build queue

DefenseManager.build()
    └─ breach patches → layout/queue → path restructuring

AttackPlanner.plan_and_execute()
    └─ shortlist → frame sim → composite score → spawn
       → outcome recording → lambda adjustment
```

Action frames (between turns) are handled by
`AlgoStrategy.on_action_frame()`, which delegates to
`StateMemory.record_action_frame()` to aggregate breach and
structure-destruction events.

---

## Module design decisions

### `state_memory.py` — `StateMemory`

**Purpose:** single source of truth for all state that must persist across
turns.  Every other module receives a `StateMemory` reference rather than
maintaining its own counters, preventing state duplication.

| Attribute | Type | Why it lives here |
|---|---|---|
| `enemy_mp_history` | `list[float]` | Scout-rush detection needs 4-turn window |
| `breach_locations` | `dict[(x,y) → count]` | Reactive defence and path restructuring |
| `enemy_attack_side` | `str` | Recomputed each turn from breach history |
| `turn_breach_count` | `int` | Reset each turn; read by `AttackPlanner` |
| `turn_structure_value_destroyed` | `float` | Reset each turn; read by `AttackPlanner` |
| `current_lambda` | `float` | Lambda weight for composite scorer; auto-adjusted |
| `last_turn_was_demolisher_push` | `bool` | Sequential-composition bridge |
| `demolisher_target_tiles` | `list` | Tiles cleared by last demolisher; checked next scout turn |
| `outcome_buffer` | `deque(maxlen=8)` | Rolling window for lambda adjustment |

**Outcome buffer schema** — each entry written by `record_attack_outcome()`:

```python
{
    "lambda_used":               float,  # lambda at decision time
    "edge_breaches":             int,    # actual breaches observed
    "structure_value_destroyed": float,  # persistence-weighted HP removed
    "frame_sim_prediction":      int,    # pre-attack sim breach count
}
```

The buffer is capped at 8 entries (`collections.deque(maxlen=8)`).  Eight
turns gives enough history to detect trends while staying within a single
typical game phase.

---

### `threat_analyzer.py` — `ThreatAnalyzer`

**Purpose:** classify the enemy's current strategy and identify which side
of their base is weakest for attack.

**Classifiers:**

- `_classify_scout_rush` — four consecutive positive MP deltas with no
  observed spend strongly indicate a scout-mass accumulation.  The 4-turn
  window balances sensitivity against false positives from normal income.

- `_classify_demolisher_line` — a horizontal wall run of ≥ 5 tiles on rows
  13–14 is the canonical demolisher fire-line setup.  The run threshold of 5
  avoids triggering on scattered wall fragments.

- `_classify_interceptor_wall` — interceptors on the enemy's front two rows
  (14–15) act as a reaction force against early scout rushes.

**Weak-side scoring** — sums turret health ratios (`health / max_health`)
separately for left (x < 14) and right (x ≥ 14) halves of the enemy
board.  Health ratio rather than raw HP is used so that a half with one
heavily damaged turret scores lower than one with a fresh turret of
identical base HP.  When sides are within 10 % of each other the method
alternates the returned side to avoid predictable attack patterns.

---

### `economy_controller.py` — `EconomyController`

**Purpose:** decide whether to attack this turn and produce an ordered SP
spending queue for `DefenseManager`.

**Attack gate** — attack fires when any of the following is true:

- Current MP ≥ 10 (enough units to form a meaningful wave)
- Projected next-turn MP is less than 90 % of current MP (MP would decay —
  better to spend now than lose it)
- Enemy health ≤ 5 (go for the kill regardless of unit count)

**SP build queue priority:**

1. W-funnel placements not yet on the board (turrets before walls, inner
   walls before outer — highest structural value per SP)
2. Turret upgrades (existing turrets gain range and damage; high ROI)
3. Wall upgrades (HP boost; lower priority than offensive upgrades)
4. Support placements at the four centre tiles (quality-of-life shielding
   for scouts; lowest priority)

The queue is pre-screened against available SP so `DefenseManager` can
execute it unconditionally without re-checking budget.

---

### `defense_manager.py` — `DefenseManager`

**Purpose:** translate the build queue into `attempt_spawn` /
`attempt_upgrade` calls and perform reactive repairs.

**W-funnel layout** (turns 0–4):

```
        [3]   [9]       [18]   [24]   <- turrets
     [2][6][7][8]  [12][13][14][15][19][20][21]  <- inner walls
  [1][0]                                [25][26][27]  <- outer walls
```

The angled walls funnel enemy units toward kill zones at `[9,9]`,
`[13,8]`, `[14,8]`, `[18,9]`.  Turrets are placed first so the kill zones
are active even if SP runs out before all walls are built.

**Reactive breach patching** — runs every turn before the main SP spend.
For each coordinate in `breach_locations` a turret is attempted one row
above (`breach_y + 1`).  This gives breach reinforcement first claim on SP.

**Path restructuring** — when a breach point has been hit ≥ 2 times the
algo walks `last_breach_path` from the enemy edge inward to find the first
unoccupied buildable tile, removes the old chokepoint walls, and places a
new wall at the intercept tile.  This forces a longer enemy path on the
next attack without permanently committing to a fixed layout.

---

### `attack_planner.py` — `AttackPlanner`

**Purpose:** select the best spawn location each attack turn using a
three-phase pipeline, then update `current_lambda` based on observed
outcomes.

#### Phase 1 — shortlist scoring

All edge spawn locations are scored on two signals:

- **Density** (`compute_structure_density`) — persistence-weighted HP of
  enemy structures within attack range along the path.  Identifies paths
  that threaten high-value targets (support ×3, turret ×2, wall ×1).
- **Safety** (`compute_survival_weighted_score`) — cumulative turret damage
  received, used to rank paths by survivability.

Top-quartile density locations are unconditionally included; remaining
slots (up to 5 total) are filled with the safest paths.  This ensures the
sim always evaluates high-value targets even when dangerous, while keeping
the shortlist small enough to fit within the turn time budget.

#### Phase 2 — frame simulation (`_simulate_frames`)

A deterministic per-frame sim walks each shortlisted path:

1. Units advance one tile per frame.
2. Units reaching the final tile are counted as edge breaches and removed.
3. Friendly support shielding is applied tile-by-tile (scout turns only).
4. Units fire at the nearest enemy structure in range (nearest → lowest-y →
   lowest-x tie-break); collective damage is applied to a mutable snapshot.
5. Turret damage is applied furthest-first within each occupied tile.
6. Dead units are removed; frame state is recorded.

The sim never modifies `game_state` — it operates on a one-time snapshot
of enemy structures built before the loop begins.

#### Phase 3 — composite scorer (`_select_best_spawn`)

```
Scout turn:      score = edge_breach_count + λ × structure_value_removed
Demolisher turn: score = structure_value_removed
```

`λ` (`current_lambda`, default 0.4) is read from `StateMemory` at call
time so the most recent auto-adjustment is always reflected.  Demolisher
turns ignore breach count because demolishers are used to open gaps, not
to score directly.

The scorer also returns `frame_sim_prediction` (the winning candidate's
`edge_breach_count`) for the lambda adjustment loop.

#### Sequential composition bridge

When the previous turn was a demolisher push, `demolisher_target_tiles`
records which enemy-structure tiles were in range.  On the following scout
turn these tiles are rechecked: if the gap is still open, spawn candidates
are restricted to the matching lateral side so scouts are directed through
the cleared corridor.

#### Lambda auto-adjustment loop (`_adjust_lambda`)

Runs every attack turn immediately after `record_attack_outcome()`.

**Accuracy gate** — MAE between `frame_sim_prediction` and `edge_breaches`
is computed across the full buffer.  If MAE > `_LAMBDA_MAE_GATE` (2.0) the
loop exits without modifying `current_lambda`.  Adjusting lambda when the
sim is wrong would reinforce the error rather than correct the scoring weight.

**Trailing consecutive run detection** — the buffer is walked from
most-recent backward; the run terminates at the first entry that breaks the
pattern:

- *Down run* — `structure_value_destroyed < 0.5` **and**
  `edge_breaches ≥ 1`: lambda is over-weighting structure value; nudge
  **down** by 0.05 per entry in the run.
- *Up run* — `edge_breaches < 1` **and**
  `structure_value_destroyed ≥ 0.5`: lambda is under-weighting structure;
  nudge **up** by 0.05 per entry in the run.

Consecutive run detection is preferred over a buffer-wide mean because a
mean masks oscillation (alternating skews cancel out), which should not
trigger an adjustment.

**Bounds:** `current_lambda` is clamped to `[0.15, 0.70]` after every
adjustment.  The floor of 0.15 keeps structure value in the score; the
ceiling of 0.70 prevents the algo from ignoring edge breaches entirely.

All threshold constants (`_SVD_NEAR_ZERO`, `_BREACH_NEAR_ZERO`,
`_LAMBDA_STEP`, `_LAMBDA_MIN`, `_LAMBDA_MAX`, `_LAMBDA_MAE_GATE`,
`_LAMBDA_MIN_BUFFER`) are defined at module level for easy tuning.

---

## Running and testing

```bash
# Local match against the starter algo (Linux/macOS)
cd scripts
./test_algo_linux.sh ../python-algo ../python-algo

# Unit tests (gamelib)
cd python-algo
python3 -m unittest discover
```

To upload, select the `python-algo` folder on the
[Terminal website](https://terminal.c1games.com).  Do **not** select the
root of the starterkit.

 │   ├──algocore.py
 │   ├──game_map.py
 │   ├──game_state.py
 │   ├──navigation.py
 │   ├──tests.py
 │   ├──unit.py
 │   └──util.py
 │
 ├──algo_strategy.py
 ├──documentation
 ├──README.md
 ├──run.ps1
 └──run.sh
```

### Creating an Algo

To create an algo, simply modify the `algo_strategy.py` file. 
To upload to terminal, upload the entire python-algo folder.

### `algo_strategy.py`

This file contains the `AlgoStrategy` class which you should modify to implement
your strategy.

At a minimum you must implement the `on_turn` method which handles responding to
the game state for each turn. Refer to the `starter_strategy` method for inspiration.

If your algo requires initialization then you should also implement the
`on_game_start` method and do any initial setup there.

### `documentation`

A directory containing the sphinx generated programming documentation, as well as the files required
to build it. You can view the docs by opening index.html in documents/_build.
You can remake the documentation by running 'make html' in the documentation folder.
You will need to install sphinx for this command to work.

### `run.sh`

A script that contains logic to invoke your code. You do not need to run this directly.
See the 'scripts' folder in the Starterkit for information about testing locally.

### `run.ps1`

A script that contains logic to invoke your code. You shouldn't need to change
this unless you change file structure or require a more customized process
startup.

### `gamelib/__init__.py`

This file tells python to treat `gamelib` as a bundled python module. This
library of functions and classes is intended to simplify development by
handling tedious tasks such as communication with the game engine, summarizing
the latest turn, and estimating paths based on the latest board state.

### `gamelib/algocore.py`

This file contains code that handles the communication between your algo and the
core game logic module. You shouldn't need to change this directly. Feel free to 
just overwrite the core methods that you would like to behave differently. 

### `gamelib/game_map.py`

This module contains the `GameMap` class which is used to parse the game state
and provide functions for querying it.

### `gamelib/navigation.py`

Functions and classes used to implement path-finding.

### `gamelib/tests.py`

Unit tests. You can write your own if you would like, and can run them using
the following command:

    python3 -m unittest discover

### `gamelib/unit.py`

This module contains the `GameUnit` class which holds information about a Unit.

### `gamelib/util.py`

Helper functions and values that do not yet have a better place to live.

## Strategy Overview

The starter strategy is designed to highlight a few common `GameMap` functions
and give the user a functioning example to work with. It's gameplan is to
draw the C1 logo, place turrets in its corners, and randomly spawn units.
