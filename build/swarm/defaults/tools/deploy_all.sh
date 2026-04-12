#!/bin/sh
set -e

PATH_STACKS=/mnt/cluster/datashares

# Ensure we don't iterate over the literal '*' if the dir is empty
for _DIR in "${PATH_STACKS}"/*
do
    if [ -d "$_DIR" ]; then
        STACK=$(basename "$_DIR")
        export STACK
        python3 /tools/deploy.py
    fi
done
