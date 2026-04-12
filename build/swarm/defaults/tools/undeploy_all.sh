#!/bin/sh
set -e

PATH_STACKS=/mnt/cluster/datashares

cleanup_stack() {
    _STACK_NAME="$1"
    echo ""
    printf "  cleanup %s ." "$_STACK_NAME"
    while true; do
        _CONTAINERS=$(docker ps -a --filter "label=com.docker.stack.namespace=$_STACK_NAME" --format "{{.ID}}")
        if [ -z "$_CONTAINERS" ]; then
            echo ""
            break
        else
            printf "."
            sleep 2
        fi
    done
}

# Remove deployment stacks
for _DIR in "${PATH_STACKS}"/*; do
    if [ -d "$_DIR" ]; then
        _STACK_NAME=$(basename "$_DIR")
        docker stack rm "$_STACK_NAME" > /dev/null 2>&1 || :
    fi
done

# Remove infra stack
docker stack rm infra > /dev/null 2>&1 || :

# Wait for cleanup
cleanup_stack infra
for _DIR in "${PATH_STACKS}"/*; do
    if [ -d "$_DIR" ]; then
        _STACK_NAME=$(basename "$_DIR")
        cleanup_stack "$_STACK_NAME"
    fi
done

docker system prune -f
