#!/bin/bash
# Start Rivendell - removes old containers and starts fresh

set -e

echo "Stopping and removing old Rivendell containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Force remove any lingering containers
docker rm -f rivendell-splunk rivendell-elasticsearch rivendell-redis rivendell-navigator \
    rivendell-backend rivendell-celery-worker rivendell-frontend rivendell-kibana 2>/dev/null || true

echo "Starting Rivendell..."
docker-compose up -d

echo ""
echo "Rivendell is starting up!"
echo ""
echo "Services:"
echo "  Frontend:      http://localhost:5687"
echo "  Backend API:   http://localhost:5688"
echo "  Splunk:        http://localhost:7755  (admin/rivendell)"
echo "  Kibana:        http://localhost:5601"
echo "  Elasticsearch: http://localhost:9200"
echo "  Navigator:     http://localhost:5602"
echo ""
echo "View logs: docker-compose logs -f"
