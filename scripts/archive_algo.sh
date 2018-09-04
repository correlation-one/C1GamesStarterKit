#!/usr/bin/env bash
echo "Archive Algo"

defaultAlgoZip=$PWD/dist/starter-algo.zip
defaultAlgoRaw=$PWD/algos/starter-algo

algoRaw=${1:-${defaultAlgoRaw}}
algoRaw=${algoRaw%/} # remove trailing slash
algoZip=${2:-${defaultAlgoZip}}

# make a duplicate directory to streamline before submission
#stagingArea=$(mktemp -d)
#cp -R "${algoRaw}" "${stagingArea}"
#cd "${stagingArea}"
#find . -mindepth 2 -maxdepth 2 --exec mv '{}' .
#rm -r "${stagingArea}/gamelib/__pycache__"
#zip -r "${algoZip}" "${stagingArea}"
#rm -r "${stagingArea}"

zip -r "${algoZip}" "${algoRaw}"

echo "Done: saved in ${algoZip}"
