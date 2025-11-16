#!/bin/bash
# Test script for Fuel Price Optimizer container

set -e

echo "=========================================="
echo "Testing Fuel Price Optimizer Container"
echo "=========================================="
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^fuel-price-optimizer$"; then
    echo "❌ Container 'fuel-price-optimizer' is not running"
    echo ""
    echo "Start it first with:"
    echo "  ./run_docker.sh"
    echo "  or"
    echo "  docker-compose up -d"
    exit 1
fi

echo "✅ Container is running"
echo ""

# Wait for API to be ready
echo "Waiting for API to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ API did not become ready within timeout"
    echo "Check logs with: docker logs fuel-price-optimizer"
    exit 1
fi

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Test 1: Health endpoint
echo "Test 1: Health Check"
echo "--------------------"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Response: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Root endpoint
echo "Test 2: Root Endpoint"
echo "--------------------"
ROOT_RESPONSE=$(curl -s http://localhost:8000/)
echo "Response: $ROOT_RESPONSE"
if echo "$ROOT_RESPONSE" | grep -q "Fuel Price Optimization"; then
    echo "✅ Root endpoint working"
else
    echo "❌ Root endpoint failed"
    exit 1
fi
echo ""

# Test 3: Recommendation endpoint
echo "Test 3: Recommendation Endpoint"
echo "-------------------------------"
RECOMMEND_RESPONSE=$(curl -s -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-31",
    "cost": 85.77,
    "comp1_price": 95.01,
    "comp2_price": 95.7,
    "comp3_price": 95.21,
    "last_price": 94.45
  }')

echo "Response: $RECOMMEND_RESPONSE"
if echo "$RECOMMEND_RESPONSE" | grep -q "recommended_price"; then
    RECOMMENDED_PRICE=$(echo "$RECOMMEND_RESPONSE" | grep -o '"recommended_price":[0-9.]*' | cut -d':' -f2)
    EXPECTED_VOLUME=$(echo "$RECOMMEND_RESPONSE" | grep -o '"expected_volume":[0-9.]*' | cut -d':' -f2)
    EXPECTED_PROFIT=$(echo "$RECOMMEND_RESPONSE" | grep -o '"expected_profit":[0-9.]*' | cut -d':' -f2)
    echo "✅ Recommendation endpoint working"
    echo ""
    echo "   Recommended Price: $RECOMMENDED_PRICE"
    echo "   Expected Volume: $EXPECTED_VOLUME liters"
    echo "   Expected Profit: $EXPECTED_PROFIT"
else
    echo "❌ Recommendation endpoint failed"
    exit 1
fi
echo ""

# Test 4: API Documentation
echo "Test 4: API Documentation"
echo "------------------------"
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ API documentation accessible at http://localhost:8000/docs"
else
    echo "⚠️  API documentation endpoint returned error"
fi
echo ""

echo "=========================================="
echo "All Tests Passed! ✅"
echo "=========================================="
echo ""
echo "Your container is working correctly!"
echo ""
echo "Access the API:"
echo "  - Health: http://localhost:8000/health"
echo "  - Docs:   http://localhost:8000/docs"
echo "  - ReDoc:  http://localhost:8000/redoc"
echo ""
echo "Useful commands:"
echo "  - View logs:   docker logs -f fuel-price-optimizer"
echo "  - Stop:        docker stop fuel-price-optimizer"
echo "  - Restart:     docker restart fuel-price-optimizer"
echo ""

