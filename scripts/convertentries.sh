#!/bin/bash

rm -f ./data/converted/*.json

for entry in ./data/exported/*.txt; do
  newname=$(basename $(sed 's/\.[^.]*$//' <<< ${entry}))
  newpath="./data/converted/${newname}.json"
  ./tools/parseentry.py "${newname}" < "${entry}" > "${newpath}"
done;
