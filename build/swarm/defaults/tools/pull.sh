#!/bin/sh
set -e

VERSION=$(cat /VERSION)
MAX_PARALLEL=5

# Function to pull an image if it doesn't exist locally
smart_pull() {
    _IMAGE="$1"
    if docker image inspect "${_IMAGE}" > /dev/null 2>&1; then
        echo " [SKIP] ${_IMAGE} already exists."
    else
        echo " [PULL] ${_IMAGE}..."
        docker pull "${_IMAGE}" > /dev/null 2>&1
        echo " [DONE] ${_IMAGE}"
    fi
}

# Collect all images to pull
MIGASFREE_IMAGES="swarm proxy certbot datashare_console datastore datastore_console database database_console core console public worker_console tunnel mcp-server pms-apt pms-yum pms-pacman pms-apk pms-wpt"
PORTAINER_IMAGES=$(grep "image:" /tools/templates/portainer.template | awk '{print $2}' | tr -d '\r')

ALL_IMAGES=""
for img in $MIGASFREE_IMAGES
do
    ALL_IMAGES="$ALL_IMAGES migasfree/${img}:${VERSION}"
done
ALL_IMAGES="$ALL_IMAGES $PORTAINER_IMAGES"

echo "Checking and pulling $(echo "$ALL_IMAGES" | wc -w) images in parallel (max $MAX_PARALLEL)..."

# Process images in batches to avoid overwhelming the system
COUNT=0
for img in $ALL_IMAGES
do
    if [ -n "$img" ]
    then
        smart_pull "$img" &
        COUNT=$((COUNT + 1))
        
        # Limit concurrency
        if [ "$COUNT" -ge "$MAX_PARALLEL" ]
        then
            wait
            COUNT=0
        fi
    fi
done

# Wait for any remaining background jobs
wait

echo "All images are up to date."
