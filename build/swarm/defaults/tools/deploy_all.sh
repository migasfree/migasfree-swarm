#!/bin/sh

PATH_STACKS=/mnt/cluster/datashares

for _DIR in ${PATH_STACKS}/*; do
  if [[ -d "$_DIR" ]]; then
    export STACK=$(basename $_DIR)
    python3 /tools/deploy.py
  fi
done
