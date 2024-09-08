#!/bin/bash

for _IMG in $(ls *.tar)
do
    docker load < ${_IMG}
done
