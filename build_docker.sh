#!/bin/bash
# Build and run script for Fuel Price Optimizer Docker container

set -e

echo "=========================================="
echo "Fuel Price Optimizer - Docker Build"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo ""
    echo "Please install Docker Desktop:"
    echo "  macOS: Download from https://www.docker.com/products/docker-desktop"
    echo "  Linux: sudo apt-get install docker.io docker-compose"
    echo ""
    exit 1
fi

# Check if model exists
if [ ! -f "models/demand_model.joblib" ]; then
    echo "⚠️  Model not found: models/demand_model.joblib"
    echo "Training model first..."
    python train_and_evaluate_model.py
fi

echo "✅ Model found: models/demand_model.joblib"

# Build the Docker image
echo ""
echo "Building Docker image..."
docker build -t fuel-price-optimizer:latest .

echo ""
echo "✅ Docker image built successfully!"
echo ""
echo "Image: fuel-price-optimizer:latest"
echo ""
echo "To run the container:"
echo "  docker run -d -p 8000:8000 --name fuel-price-optimizer fuel-price-optimizer:latest"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up -d"

