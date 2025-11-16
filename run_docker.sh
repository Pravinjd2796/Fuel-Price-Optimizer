#!/bin/bash
# Run Docker container for Fuel Price Optimizer

set -e

echo "=========================================="
echo "Fuel Price Optimizer - Docker Run"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if image exists
if ! docker image inspect fuel-price-optimizer:latest &> /dev/null; then
    echo "⚠️  Docker image not found. Building first..."
    ./build_docker.sh
fi

# Stop and remove existing container if running
if docker ps -a --format '{{.Names}}' | grep -q "^fuel-price-optimizer$"; then
    echo "Stopping existing container..."
    docker stop fuel-price-optimizer 2>/dev/null || true
    docker rm fuel-price-optimizer 2>/dev/null || true
fi

# Run the container
echo ""
echo "Starting container..."
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/outputs:/app/outputs" \
  --name fuel-price-optimizer \
  --restart unless-stopped \
  fuel-price-optimizer:latest

echo ""
echo "✅ Container started successfully!"
echo ""
echo "Container name: fuel-price-optimizer"
echo "API available at: http://localhost:8000"
echo ""
echo "Useful commands:"
echo "  View logs:        docker logs -f fuel-price-optimizer"
echo "  Stop container:   docker stop fuel-price-optimizer"
echo "  Remove container: docker rm fuel-price-optimizer"
echo "  Health check:     curl http://localhost:8000/health"
echo ""
echo "Waiting for container to be ready..."
sleep 5

# Health check
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is healthy and ready!"
    echo ""
    echo "Test the API:"
    echo "  curl http://localhost:8000/health"
    echo "  curl http://localhost:8000/docs"
else
    echo "⚠️  Container started but API not ready yet. Check logs:"
    echo "   docker logs fuel-price-optimizer"
fi

