#!/bin/bash


cd /app/backend

init-assistant &

reload_proxy 30
bash start.sh
