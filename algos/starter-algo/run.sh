#!/bin/bash

# TODO: this is not robust, make better
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
${PYTHON_CMD:-python3} -u "$DIR/algo_strategy.py"
