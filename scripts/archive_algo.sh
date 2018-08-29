#!/usr/bin/env bash
echo "Archive Algo"
defaultAlgoZip=$PWD/dist/starter-algo.zip
defaultAlgoRaw=$PWD/algos/starter-algo

algoZip=${1:-${defaultAlgoZip}}
algoRaw=${2:-${defaultAlgoRaw}}

echo "Archiving: ${algoRaw}" 
zip -r ${algoZip} ${algoRaw}

echo "Done: saved in ${algoZip}"
