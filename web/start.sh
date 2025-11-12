#!/bin/bash

# Elrond Web Interface Startup Script

set -e

echo "🧙‍♂️ Starting Elrond Web Interface..."

# Check if Docker is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend configuration..."
    cp backend/.env.example backend/.env
    echo "✅ Configuration file created at backend/.env"
    echo "   You can edit this file to customize settings"
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "🏗️  Building containers (this may take a few minutes on first run)..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Elrond Web Interface is now running!"
    echo ""
    echo "📍 Access points:"
    echo "   • Frontend:  http://localhost:3000"
    echo "   • Backend:   http://localhost:8000"
    echo "   • API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📋 Useful commands:"
    echo "   • View logs:     docker-compose logs -f"
    echo "   • Stop:          docker-compose down"
    echo "   • Restart:       docker-compose restart"
    echo ""
    echo "🔍 To view real-time logs, run:"
    echo "   docker-compose logs -f"
else
    echo ""
    echo "❌ Error: Services failed to start"
    echo "Run 'docker-compose logs' to see error details"
    exit 1
fi
