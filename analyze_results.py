#!/usr/bin/env python3
"""
analyze_results.py — Parse sweep replays and produce a results CSV + summary.

Usage:
    python3 analyze_results.py                       # default: replays/sweep/
    python3 analyze_results.py --dir replays/sweep/   # explicit path
    python3 analyze_results.py --csv results.csv      # custom output file

Reads every .replay file in the directory, extracts metrics from endStats,
and writes:
  • A CSV file (sweep_results.csv by default)
  • A formatted summary table to stdout
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(ROOT, "replays", "sweep")


def parse_replay(path: str) -> dict | None:
    """
    Parse a .replay file (newline-delimited JSON).
    Returns a dict of extracted metrics, or None on error.
    """
    try:
        with open(path, "r") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except Exception as e:
        print(f"  WARNING: could not read {path}: {e}")
        return None

    # Extract aggression from filename: aggression_0.30_run1.replay
    basename = os.path.basename(path)
    m = re.search(r"aggression_([\d.]+)_run(\d+)", basename)
    if m:
        aggression = float(m.group(1))
        run_id = int(m.group(2))
    else:
        aggression = None
        run_id = None

    # Find endStats (last parseable JSON object that has endStats)
    end_stats = None
    turn_data = []

    for line in lines:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        if "endStats" in obj:
            end_stats = obj["endStats"]

        # Collect turn-by-turn resource data (turnInfo[0] == 0 = deploy phase)
        if "turnInfo" in obj and obj["turnInfo"][0] == 0:
            turn_num = obj["turnInfo"][1]
            p1 = obj.get("p1Stats", [0, 0, 0, 0])
            p2 = obj.get("p2Stats", [0, 0, 0, 0])
            turn_data.append({
                "turn": turn_num,
                "p1_health": p1[0], "p1_sp": p1[1], "p1_mp": p1[2],
                "p2_health": p2[0], "p2_sp": p2[1], "p2_mp": p2[2],
            })

    if end_stats is None:
        print(f"  WARNING: no endStats in {path}")
        return None

    # Extract fields — endStats uses player1/player2 sub-objects
    winner_id = end_stats.get("winner", -1)  # 1 or 2
    duration = end_stats.get("turns", 0)

    p1 = end_stats.get("player1", {})
    p2 = end_stats.get("player2", {})

    # Our agent is always player 1 (first arg to engine)
    return {
        "aggression": aggression,
        "run": run_id,
        "winner": "agent" if winner_id == 1 else "opponent" if winner_id == 2 else "unknown",
        "agent_points": p1.get("points_scored", 0),
        "opponent_points": p2.get("points_scored", 0),
        "turns": duration,
        "agent_sp_spent": p1.get("stationary_resource_spent", 0),
        "agent_mp_spent": p1.get("dynamic_resource_spent", 0),
        "agent_mp_wasted": p1.get("dynamic_resource_spoiled", 0),
        "agent_sp_on_board": p1.get("stationary_resource_left_on_board", 0),
        "opponent_sp_spent": p2.get("stationary_resource_spent", 0),
        "opponent_mp_spent": p2.get("dynamic_resource_spent", 0),
        "agent_crashed": p1.get("crashed", False),
        "opponent_crashed": p2.get("crashed", False),
        "replay_file": basename,
        "turn_count": len(turn_data),
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze sweep replay files")
    parser.add_argument("--dir", default=DEFAULT_DIR,
                        help="Directory containing .replay files")
    parser.add_argument("--csv", default="sweep_results.csv",
                        help="Output CSV filename (default: sweep_results.csv)")
    args = parser.parse_args()

    replay_files = sorted(glob.glob(os.path.join(args.dir, "*.replay")))
    if not replay_files:
        print(f"No .replay files found in {args.dir}")
        sys.exit(1)

    print(f"Found {len(replay_files)} replay files in {args.dir}\n")

    results = []
    for path in replay_files:
        row = parse_replay(path)
        if row:
            results.append(row)

    if not results:
        print("No results could be parsed.")
        sys.exit(1)

    # Sort by aggression, then run
    results.sort(key=lambda r: (r["aggression"] or 0, r["run"] or 0))

    # Write CSV
    csv_path = os.path.join(ROOT, args.csv)
    fieldnames = list(results[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"CSV written to {csv_path}\n")

    # Print summary table
    print("═" * 100)
    print(f"{'Aggr':>6}  {'Run':>3}  {'Winner':>8}  {'Agent Pts':>9}  {'Opp Pts':>7}  "
          f"{'Turns':>5}  {'SP Spent':>8}  {'MP Spent':>8}  {'MP Wasted':>9}  {'SP Board':>8}")
    print("─" * 100)
    for r in results:
        print(f"{r['aggression']:>6.2f}  {r['run']:>3}  {r['winner']:>8}  "
              f"{r['agent_points']:>9.0f}  {r['opponent_points']:>7.0f}  "
              f"{r['turns']:>5}  {r['agent_sp_spent']:>8.0f}  "
              f"{r['agent_mp_spent']:>8.0f}  {r['agent_mp_wasted']:>9.1f}  "
              f"{r['agent_sp_on_board']:>8.0f}")
    print("═" * 100)

    # Aggregate stats by aggression value
    from collections import defaultdict
    by_aggr = defaultdict(list)
    for r in results:
        by_aggr[r["aggression"]].append(r)

    print(f"\n{'Aggr':>6}  {'Matches':>7}  {'Win%':>5}  {'Avg Agent Pts':>13}  "
          f"{'Avg Opp Pts':>11}  {'Avg Turns':>9}")
    print("─" * 65)
    for aggr in sorted(by_aggr.keys()):
        rows = by_aggr[aggr]
        n = len(rows)
        wins = sum(1 for r in rows if r["winner"] == "agent")
        avg_ap = sum(r["agent_points"] for r in rows) / n
        avg_op = sum(r["opponent_points"] for r in rows) / n
        avg_turns = sum(r["turns"] for r in rows) / n
        print(f"{aggr:>6.2f}  {n:>7}  {100*wins/n:>4.0f}%  {avg_ap:>13.1f}  "
              f"{avg_op:>11.1f}  {avg_turns:>9.1f}")
    print("═" * 65)
    print(f"\nTotal: {len(results)} matches across {len(by_aggr)} aggression levels")


if __name__ == "__main__":
    main()
