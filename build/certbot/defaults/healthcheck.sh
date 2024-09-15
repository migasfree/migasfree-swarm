#!/bin/sh

pgrep -f '/docker-entrypoint.sh' >/dev/null || exit 1