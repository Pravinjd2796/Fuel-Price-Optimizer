#!/bin/bash
# Verification script for Docker installation and Fuel Price Optimizer container

set -e

echo "=========================================="
echo "Docker Installation Verification"
echo "=========================================="
echo ""

# Check Docker installation
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "   ✅ Docker is installed: $DOCKER_VERSION"
else
    echo "   ❌ Docker is not installed or not in PATH"
    echo "   Please install Docker Desktop first."
    echo "   See INSTALL_DOCKER.md for instructions."
    exit 1
fi

# Check Docker Compose
echo ""
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "   ✅ Docker Compose is installed: $COMPOSE_VERSION"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo "   ✅ Docker Compose (plugin) is installed: $COMPOSE_VERSION"
else
    echo "   ⚠️  Docker Compose not found (optional, but recommended)"
fi

# Check if Docker daemon is running
echo ""
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo "   ✅ Docker daemon is running"
else
    echo "   ❌ Docker daemon is not running"
    echo "   Please start Docker Desktop and wait for it to be ready."
    exit 1
fi

# Test Docker with hello-world
echo ""
echo "4. Testing Docker with hello-world container..."
if docker run --rm hello-world &> /dev/null; then
    echo "   ✅ Docker is working correctly"
else
    echo "   ⚠️  Could not run hello-world container (may need to pull image)"
    echo "   This is usually fine, continuing..."
fi

# Check if model exists
echo ""
echo "5. Checking for trained model..."
if [ -f "models/demand_model.joblib" ]; then
    MODEL_SIZE=$(ls -lh models/demand_model.joblib | awk '{print $5}')
    echo "   ✅ Model found: models/demand_model.joblib ($MODEL_SIZE)"
else
    echo "   ⚠️  Model not found: models/demand_model.joblib"
    echo "   The Docker build will fail without a trained model."
    echo "   Run: python train_and_evaluate_model.py"
    exit 1
fi

# Check if Dockerfile exists
echo ""
echo "6. Checking Docker configuration files..."
if [ -f "Dockerfile" ]; then
    echo "   ✅ Dockerfile found"
else
    echo "   ❌ Dockerfile not found"
    exit 1
fi

if [ -f "docker-compose.yml" ]; then
    echo "   ✅ docker-compose.yml found"
else
    echo "   ⚠️  docker-compose.yml not found (optional)"
fi

if [ -f ".dockerignore" ]; then
    echo "   ✅ .dockerignore found"
else
    echo "   ⚠️  .dockerignore not found (optional)"
fi

# Check if image already exists
echo ""
echo "7. Checking for existing Docker image..."
if docker image inspect fuel-price-optimizer:latest &> /dev/null; then
    IMAGE_SIZE=$(docker image inspect fuel-price-optimizer:latest --format='{{.Size}}' | numfmt --to=iec-i --suffix=B 2>/dev/null || docker image inspect fuel-price-optimizer:latest --format='{{.Size}}')
    echo "   ✅ Docker image exists: fuel-price-optimizer:latest ($IMAGE_SIZE)"
    echo "   You can skip the build step and run directly."
else
    echo "   ⚠️  Docker image not found: fuel-price-optimizer:latest"
    echo "   You'll need to build it first: ./build_docker.sh"
fi

# Check if container is running
echo ""
echo "8. Checking for running container..."
if docker ps --format '{{.Names}}' | grep -q "^fuel-price-optimizer$"; then
    echo "   ✅ Container 'fuel-price-optimizer' is running"
    
    # Test the API
    echo ""
    echo "9. Testing API endpoint..."
    sleep 2
    if curl -s http://localhost:8000/health > /dev/null; then
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
        echo "   ✅ API is healthy: $HEALTH_RESPONSE"
    else
        echo "   ⚠️  API endpoint not responding yet (may still be starting)"
    fi
else
    echo "   ℹ️  Container 'fuel-price-optimizer' is not running"
    echo "   Start it with: ./run_docker.sh or docker-compose up -d"
fi

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "Next steps:"
if ! docker image inspect fuel-price-optimizer:latest &> /dev/null; then
    echo "  1. Build the Docker image: ./build_docker.sh"
fi
if ! docker ps --format '{{.Names}}' | grep -q "^fuel-price-optimizer$"; then
    echo "  2. Run the container: ./run_docker.sh"
fi
echo "  3. Test the API: curl http://localhost:8000/health"
echo "  4. View API docs: open http://localhost:8000/docs"
echo ""

