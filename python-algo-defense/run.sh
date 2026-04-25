#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
STRATEGY=defense ${PYTHON_CMD:-python3} -u "$DIR/algo_strategy.py"
