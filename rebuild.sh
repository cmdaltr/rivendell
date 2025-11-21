#!/bin/bash
# Rivendell Docker Image Rebuild Script
# This script rebuilds the Docker images to apply the latest changes

set -e  # Exit on error

echo "=========================================="
echo "Rivendell Docker Image Rebuild"
echo "=========================================="
echo ""

# Stop all containers
echo "Step 1/4: Stopping all containers..."
docker-compose down
echo "✓ Containers stopped"
echo ""

# Rebuild images (this will take 15-20 minutes)
echo "Step 2/4: Rebuilding images (this may take 15-20 minutes)..."
echo "           - Compiling apfs-fuse from source"
echo "           - Installing Volatility3 with symbol tables"
echo ""
docker-compose build --no-cache
echo "✓ Images rebuilt"
echo ""

# Start services
echo "Step 3/4: Starting services..."
docker-compose up -d
echo "✓ Services started"
echo ""

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 10

# Verify installations
echo "Step 4/4: Verifying installations..."
echo ""

echo "Checking apfs-fuse installation:"
if docker exec rivendell-app which apfs-fuse > /dev/null 2>&1; then
    echo "✓ apfs-fuse is installed at: $(docker exec rivendell-app which apfs-fuse)"
else
    echo "✗ apfs-fuse not found"
fi
echo ""

echo "Checking Volatility3 installation:"
if docker exec rivendell-app vol3 --help > /dev/null 2>&1; then
    echo "✓ Volatility3 is installed and accessible via 'vol3'"
else
    echo "✗ Volatility3 not found"
fi
echo ""

echo "=========================================="
echo "Rebuild Complete!"
echo "=========================================="
echo ""
echo "Your Rivendell instance is now running with:"
echo "  - apfs-fuse for macOS APFS filesystem support"
echo "  - Volatility3 for memory analysis"
echo ""
echo "You can access the web interface at: http://localhost:3000"
echo ""
