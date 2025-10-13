#!/bin/sh

PATH_STACKS=/mnt/cluster/datashares

function cleanup_stack {
    local STACK_NAME="$1"
    echo ""
    echo -n "  cleanup $STACK_NAME ."
    while true; do
        CONTAINERS=$(docker ps -a --filter "label=com.docker.stack.namespace=$STACK_NAME" --format "{{.ID}}")
        if [ -z "$CONTAINERS" ]; then
            echo ""
            break
        else
            echo -n "."
            sleep 2
        fi
    done
}

for STACK in ${PATH_STACKS}/*; do
  if [[ -d "$STACK" ]]; then
    docker stack rm $(basename $STACK)
  fi
done
docker stack rm infra


cleanup_stack infra
for STACK in ${PATH_STACKS}/*; do
  if [[ -d "$STACK" ]]; then
    cleanup_stack $(basename $STACK)
  fi
done



docker system prune -f
