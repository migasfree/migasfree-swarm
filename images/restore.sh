#!/bin/bash

for _IMG in ./*.tar
do
    [ -e "$_IMG" ] || continue
    docker load < "$_IMG"
done
