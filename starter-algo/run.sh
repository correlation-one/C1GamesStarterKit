#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
${PYTHON_CMD:-python3} -u "$DIR/algo_strategy.py"

#Keep this here so that process stays alive and you can read error debug information on the website
while true; do
  	sleep 5
done