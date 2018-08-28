#!/usr/bin/env bash
echo "Starting script"
location=$PWD
algo1=$1
algo2=$2
[[ ! -z "$1" ]] || echo "Using default location for algo1" && algo1=${location}/starter-algo/run.sh
[[ ! -z "$2" ]] || echo "Using default location for algo2" && algo2=${location}/starter-algo/run.sh
#if [[ ! $1 ]]; then echo "Using default location for algo1" #&& algo1=${location}/starter-algo
#if [[ ! $2 ]]; then echo "Using default location for algo1" #&& algo1=${location}/starter-algo
echo "Algo1: ${algo1}"
echo "Algo2: ${algo2}"
echo "Starting Engine"
java -jar engine.jar work ${algo1} ${algo2}