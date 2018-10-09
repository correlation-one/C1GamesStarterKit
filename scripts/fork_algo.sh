#!/usr/bin/env bash
echo "Fork Algo"

defaultAlgo=$PWD/algos/starter-algo-ZIPME
defaultTarget=$PWD/algos/renamed-algo

algoSrc=${1:-${defaultAlgo}}
algoSrc=${algoSrc%/}
algoDest=${2:-${defaultTarget}}
algoDest=${algoDest%/}

echo "Copying algo at ${algoSrc} to ${algoDest}..." 
cp -R "${algoSrc}" "${algoDest}"

echo "Done. Make modifications to files in ${algoDest} to customize your new algo"
