#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
${PYTHON_CMD:-python3} -u "$DIR/algo_strategy.py"

# Keep alive long enough to pass any errors/debug info to replay visualizer
while true; do
  	sleep 5
done