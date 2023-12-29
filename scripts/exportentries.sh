#!/bin/bash

set -e

rm -f ./data/exported/*.txt

while read p; do
  outp1=$(sed 's/[\/\|]/::/g' <<< $p)
  outp2=$(sed 's/\s+/-/g' <<< $outp1)
  pass show "${p}" > "./data/exported/${outp2}.txt"
done < ./data/summary/paths.txt
