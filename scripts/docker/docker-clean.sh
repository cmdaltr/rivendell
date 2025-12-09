#!/bin/bash
# Deep clean Docker - removes all unused resources to reclaim disk space
# Safe to run - won't affect running containers or their volumes

set -e

echo "=== Docker Cleanup Script ==="
echo ""
echo "Current Docker disk usage:"
docker system df
echo ""

# Ask for confirmation unless -f flag is passed
if [[ "$1" != "-f" ]]; then
    read -p "This will remove unused images, build cache, and orphan volumes. Continue? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "1. Removing dangling images..."
docker image prune -f

echo ""
echo "2. Removing unused images (not used by any container)..."
docker image prune -af

echo ""
echo "3. Removing build cache..."
docker builder prune -af

echo ""
echo "4. Removing orphan volumes (not used by any container)..."
docker volume prune -f

echo ""
echo "5. Removing unused networks..."
docker network prune -f

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Final Docker disk usage:"
docker system df
