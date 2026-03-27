#!/bin/bash
# ─────────────────────────────────────────────────────────────
# run_experiments.sh — Run all 3 matchups between the agent variants.
#
# Creates replay files in the replays/ directory that can be
# viewed at https://terminal.c1games.com/playground
#
# Usage:  ./run_experiments.sh
# ─────────────────────────────────────────────────────────────

set -e

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir -p "$ROOT/replays"

echo "========================================"
echo " MATCH 1: baseline  vs  offense"
echo "========================================"
cd "$ROOT" && java -jar engine.jar work \
    "$ROOT/python-algo/run.sh" \
    "$ROOT/python-algo-offense/run.sh"
echo ""

echo "========================================"
echo " MATCH 2: baseline  vs  defense"
echo "========================================"
cd "$ROOT" && java -jar engine.jar work \
    "$ROOT/python-algo/run.sh" \
    "$ROOT/python-algo-defense/run.sh"
echo ""

echo "========================================"
echo " MATCH 3: offense  vs  defense"
echo "========================================"
cd "$ROOT" && java -jar engine.jar work \
    "$ROOT/python-algo-offense/run.sh" \
    "$ROOT/python-algo-defense/run.sh"
echo ""

echo "========================================"
echo " All matches complete!"
echo " Replay files are in: $ROOT/replays/"
echo "========================================"
