#!/bin/bash

nested="./starter-algo-master"

{
  source=$(git rev-parse --show-toplevel)
} || {
  echo "Please make sure you are in the starter-algo directory."
  exit 1
}

temp=$(mktemp -d)
pushd $temp

git clone $source $nested
rm -rf $nested/.git
rm $nested/.gitignore
zip -r starter-algo.zip $nested
mv starter-algo.zip ${source}/my-algo-archive.zip

popd
rm -rf $temp
