# Docker Deployment Guide

This guide explains how to deploy the Fuel Price Optimizer using Docker.

## Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 1.29+)
- Trained model file: `models/demand_model.joblib`

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode (background):**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t fuel-price-optimizer .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name fuel-price-optimizer \
     -p 8000:8000 \
     -v $(pwd)/outputs:/app/outputs \
     fuel-price-optimizer
   ```

3. **View logs:**
   ```bash
   docker logs -f fuel-price-optimizer
   ```

4. **Stop the container:**
   ```bash
   docker stop fuel-price-optimizer
   docker rm fuel-price-optimizer
   ```

## Verify Deployment

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test recommendation endpoint:**
   ```bash
   curl -X POST http://localhost:8000/recommend \
     -H "Content-Type: application/json" \
     -d '{
       "date": "2024-12-31",
       "cost": 85.77,
       "comp1_price": 95.01,
       "comp2_price": 95.7,
       "comp3_price": 95.21,
       "last_price": 94.45
     }'
   ```

3. **Access interactive API docs:**
   Open browser: http://localhost:8000/docs

## Important Notes

### Model Requirement

⚠️ **Before building the Docker image, ensure you have a trained model:**
```bash
# Train the model first
python train_and_evaluate_model.py

# Verify model exists
ls -lh models/demand_model.joblib
```

The Docker image includes the model in the build. If you want to update the model without rebuilding:
1. Mount the models directory as a volume in `docker-compose.yml`
2. Update the model file in the mounted directory

### Data Files

The Docker image includes:
- `data/oil_retail_history.csv` - Historical training data
- `models/demand_model.joblib` - Trained model

If you want to update data without rebuilding:
1. Uncomment the volume mounts in `docker-compose.yml`
2. Update the files in your local directories

### Outputs Directory

The `outputs/` directory is mounted as a volume, so recommendations saved by the API will persist on your host machine.

## Production Deployment

### Environment Variables

You can customize the deployment using environment variables in `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - API_PORT=8000
  - LOG_LEVEL=info
```

### Security Considerations

1. **Don't expose port 8000 publicly** - Use a reverse proxy (nginx, traefik) with HTTPS
2. **Update dependencies regularly** - Rebuild image with updated requirements.txt
3. **Limit resources** - Add resource limits in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Scaling

To run multiple instances behind a load balancer:

```yaml
services:
  fuel-price-api:
    # ... existing configuration ...
    deploy:
      replicas: 3
```

## Troubleshooting

### Container won't start

1. **Check if model exists:**
   ```bash
   ls -lh models/demand_model.joblib
   ```

2. **Check container logs:**
   ```bash
   docker-compose logs fuel-price-api
   ```

3. **Check if port 8000 is already in use:**
   ```bash
   lsof -i :8000
   ```
   Change the port in `docker-compose.yml` if needed.

### Model not found error

The model must be present before building. If you see "Model not found":
1. Train the model: `python train_and_evaluate_model.py`
2. Rebuild the image: `docker-compose build --no-cache`

### Permission errors

If you encounter permission errors with volumes:
```bash
sudo chown -R $USER:$USER outputs/
```

## Building for Different Architectures

### Build for ARM64 (Apple Silicon, Raspberry Pi):
```bash
docker buildx build --platform linux/arm64 -t fuel-price-optimizer .
```

### Build for AMD64:
```bash
docker buildx build --platform linux/amd64 -t fuel-price-optimizer .
```

## Development with Docker

For development with hot-reload:

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  fuel-price-api:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./src:/app/src  # Mount source code for hot-reload
    command: uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

Run with:
```bash
docker-compose -f docker-compose.dev.yml up
```

## Image Size Optimization

The current Dockerfile uses a multi-stage build to minimize image size. To further optimize:

1. Use Alpine Linux (smaller base image, but may have compatibility issues):
   ```dockerfile
   FROM python:3.11-alpine
   ```

2. Remove unnecessary packages after installation
3. Use `.dockerignore` to exclude files (already configured)

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t fuel-price-optimizer .
      - name: Run tests
        run: docker run fuel-price-optimizer pytest tests/
```

---

For more information, see the main [STEPS_TO_RUN.md](STEPS_TO_RUN.md) and [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md).

