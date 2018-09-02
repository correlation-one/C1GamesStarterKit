#!/usr/bin/env bash
echo "Fork Algo"

defaultAlgo=$PWD/algos/starter-algo
defaultTarget=$PWD/algos/renamed-algo

algoSrc=${1:-${defaultAlgo}}
algoDest=${2:-${defaultTarget}}

echo "Copying algo at ${algoSrc} to ${algoDest}..." 
cp -R "${algoSrc}" "${algoDest}"

echo "Done. Make modifications to files in ${algoDest} to customize your new algo"
