#!/bin/bash
# Rebuild and start Rivendell - removes old containers, rebuilds images, and starts fresh

set -e

echo "Stopping and removing old Rivendell containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Force remove any lingering containers
docker rm -f rivendell-splunk rivendell-elasticsearch rivendell-redis rivendell-navigator \
    rivendell-backend rivendell-celery-worker rivendell-frontend rivendell-kibana \
    rivendell-elasticsearch-setup 2>/dev/null || true

# Clean up Docker to prevent disk bloat
echo ""
echo "Cleaning up Docker (removing unused images, build cache, and orphan volumes)..."
docker image prune -f 2>/dev/null || true
docker builder prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true

echo ""
echo "Rebuilding Rivendell images..."
docker-compose build --no-cache

echo ""
echo "Starting Rivendell..."
docker-compose up -d

echo ""
echo "Rivendell is starting up!"
echo ""
echo "Services:"
echo "  Frontend:      http://localhost:5687"
echo "  Backend API:   http://localhost:5688"
echo "  Splunk:        http://localhost:7755  (admin/rivendell)"
echo "  Kibana:        http://localhost:5601  (admin/rivendell)"
echo "  Elasticsearch: http://localhost:9200  (admin/rivendell)"
echo "  Navigator:     http://localhost:5602"
echo ""
echo "View logs: docker-compose logs -f"
echo ""
echo "To clean up Docker disk space: scripts/docker-clean.sh"
