#!/usr/bin/env bash
echo "Run Match"
defaultAlgo=$PWD/python-algo

algo1=${1:-${defaultAlgo}}
algo1=${algo1%/}
algo2=${2:-${defaultAlgo}}
algo2=${algo2%/}

echo "P1: ${algo1}"
echo "P2: ${algo2}"
echo "Starting Match: ${algo1} vs. ${algo2}"
java -jar engine.jar work ${algo1}/run.sh ${algo2}/run.sh
