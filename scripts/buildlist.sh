#!/bin/bash

set -e

(
  cd ~/.password-store \
  && \
  find \
    . \
    -type f \
    -not -ipath './.*' \
    -exec realpath --relative-to ./ {} \;
) \
| sed 's/\.[^.]*$//' \
> ./data/summary/paths.txt
