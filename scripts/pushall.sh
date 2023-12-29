#!/bin/bash

for entry in ./data/converted/*.json; do
  ./tools/pushtoop.py < "${entry}"
done;
