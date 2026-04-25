#!/usr/bin/env python3
"""
run_sweep.py — Parameter sweep: run agents at various aggression levels
                against the fixed starter opponent.

Usage:
    python3 run_sweep.py                   # default 11 values (0.0, 0.1, … 1.0)
    python3 run_sweep.py --steps 5         # 5 values (0.0, 0.25, 0.5, 0.75, 1.0)
    python3 run_sweep.py --values 0.2 0.5 0.8  # specific values
    python3 run_sweep.py --repeats 3       # run each value 3 times

For each aggression value the script:
  1. Creates a temp algo directory with a run.sh that exports AGGRESSION=<value>
  2. Runs `java -jar engine.jar work <temp>/run.sh python-algo-starter/run.sh`
  3. Moves the resulting .replay file to replays/sweep/

After all matches, prints a summary and points you to analyze_results.py.
"""

import argparse
import glob
import os
import shutil
import stat
import subprocess
import sys
import textwrap
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
ALGO_SRC = os.path.join(ROOT, "python-algo")
OPPONENT = os.path.join(ROOT, "python-algo-starter")
ENGINE   = os.path.join(ROOT, "engine.jar")
REPLAY_DIR = os.path.join(ROOT, "replays", "sweep")


def make_algo_dir(aggression: float, run_id: int) -> str:
    """
    Create a temporary algo directory for a specific aggression value.
    Symlinks gamelib/ and strategies/ to avoid copying code.
    Copies algo_strategy.py and algo.json.
    Writes a custom run.sh that exports AGGRESSION.
    """
    name = f"sweep_a{aggression:.2f}_r{run_id}"
    dest = os.path.join(ROOT, ".sweep_tmp", name)
    os.makedirs(dest, exist_ok=True)

    # Symlink shared code directories
    for dirname in ("gamelib", "strategies"):
        src = os.path.join(ALGO_SRC, dirname)
        dst = os.path.join(dest, dirname)
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(src, dst)

    # Copy entry-point files
    for fname in ("algo_strategy.py", "algo.json"):
        src = os.path.join(ALGO_SRC, fname)
        dst = os.path.join(dest, fname)
        shutil.copy2(src, dst)

    # Write run.sh with AGGRESSION env var
    run_sh = os.path.join(dest, "run.sh")
    with open(run_sh, "w") as f:
        f.write(textwrap.dedent(f"""\
            #!/bin/bash
            export AGGRESSION={aggression:.4f}
            DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
            ${{PYTHON_CMD:-python3}} -u "$DIR/algo_strategy.py"
        """))
    os.chmod(run_sh, os.stat(run_sh).st_mode | stat.S_IEXEC)

    return dest


def find_latest_replay() -> str | None:
    """Find the most recently created .replay file in replays/."""
    pattern = os.path.join(ROOT, "replays", "*.replay")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def run_match(algo_dir: str, aggression: float, run_id: int) -> str | None:
    """Run a match and return the path to the replay file, or None on error."""
    print(f"  ▶ aggression={aggression:.2f}  run={run_id} ...", end=" ", flush=True)
    t0 = time.time()

    before_replays = set(glob.glob(os.path.join(ROOT, "replays", "*.replay")))

    result = subprocess.run(
        ["java", "-jar", ENGINE, "work",
         os.path.join(algo_dir, "run.sh"),
         os.path.join(OPPONENT, "run.sh")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"FAILED (exit {result.returncode})")
        err_log = os.path.join(algo_dir, "engine_err.log")
        with open(err_log, "w") as f:
            f.write(result.stderr)
        print(f"    stderr saved to {err_log}")
        return None

    # Find the new replay file
    after_replays = set(glob.glob(os.path.join(ROOT, "replays", "*.replay")))
    new_replays = after_replays - before_replays

    if not new_replays:
        # Fallback: use most recent
        replay = find_latest_replay()
    else:
        replay = max(new_replays, key=os.path.getmtime)

    elapsed = time.time() - t0
    print(f"done ({elapsed:.1f}s)")

    if replay:
        # Move replay into sweep directory with a descriptive name
        dest_name = f"aggression_{aggression:.2f}_run{run_id}.replay"
        dest_path = os.path.join(REPLAY_DIR, dest_name)
        shutil.move(replay, dest_path)
        return dest_path

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Sweep aggression parameter against a fixed opponent")
    parser.add_argument("--steps", type=int, default=11,
                        help="Number of evenly spaced aggression values (default 11 → 0.0..1.0)")
    parser.add_argument("--values", type=float, nargs="+",
                        help="Explicit aggression values to test (overrides --steps)")
    parser.add_argument("--repeats", type=int, default=1,
                        help="How many times to repeat each value (default 1)")
    args = parser.parse_args()

    # Determine aggression values
    if args.values:
        values = sorted(set(args.values))
    else:
        values = [round(i / (args.steps - 1), 4) for i in range(args.steps)]

    total = len(values) * args.repeats
    print(f"═══ Parameter Sweep ═══")
    print(f"  Aggression values: {[f'{v:.2f}' for v in values]}")
    print(f"  Repeats per value: {args.repeats}")
    print(f"  Total matches:     {total}")
    print(f"  Opponent:          python-algo-starter")
    print()

    # Pre-flight checks
    if not os.path.isfile(ENGINE):
        print(f"ERROR: engine.jar not found at {ENGINE}")
        sys.exit(1)
    if not os.path.isdir(OPPONENT):
        print(f"ERROR: opponent dir not found at {OPPONENT}")
        sys.exit(1)

    # Ensure output dir exists
    os.makedirs(REPLAY_DIR, exist_ok=True)

    # Clean old sweep tmp dirs
    sweep_tmp = os.path.join(ROOT, ".sweep_tmp")
    if os.path.exists(sweep_tmp):
        shutil.rmtree(sweep_tmp)

    results = []
    for aggression in values:
        for run_id in range(1, args.repeats + 1):
            algo_dir = make_algo_dir(aggression, run_id)
            replay = run_match(algo_dir, aggression, run_id)
            results.append({
                "aggression": aggression,
                "run": run_id,
                "replay": replay,
            })

    # Cleanup temp dirs
    if os.path.exists(sweep_tmp):
        shutil.rmtree(sweep_tmp)

    # Summary
    successes = sum(1 for r in results if r["replay"])
    print()
    print(f"═══ Sweep Complete ═══")
    print(f"  {successes}/{total} matches succeeded")
    print(f"  Replays saved in: {REPLAY_DIR}")
    print()
    if successes > 0:
        print("  Next step: python3 analyze_results.py")


if __name__ == "__main__":
    main()
