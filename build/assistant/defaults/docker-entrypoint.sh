#!/bin/bash


cd /app/backend

init-assistant &

reload_proxy 5
bash start.sh
