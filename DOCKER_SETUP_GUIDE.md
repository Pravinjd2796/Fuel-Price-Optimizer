# Complete Docker Setup Guide

This guide will help you install Docker, build the container, and verify everything works.

## Quick Start Checklist

- [ ] Step 1: Install Docker Desktop
- [ ] Step 2: Verify Docker installation
- [ ] Step 3: Build Docker image
- [ ] Step 4: Run container
- [ ] Step 5: Test the API

---

## Step 1: Install Docker Desktop

### For macOS:

**Option A: Using Homebrew (Recommended)**
```bash
brew install --cask docker
```

**Option B: Manual Download**
1. Visit: https://www.docker.com/products/docker-desktop
2. Download Docker Desktop for Mac (Apple Silicon or Intel)
3. Open the `.dmg` file and drag Docker to Applications
4. Launch Docker Desktop from Applications

**After Installation:**
- Look for the Docker whale icon in the menu bar
- Wait until the icon stops animating (Docker is ready)
- You may be asked to authorize Docker Desktop

### For Linux:
See detailed instructions in `INSTALL_DOCKER.md`

### For Windows:
See detailed instructions in `INSTALL_DOCKER.md`

---

## Step 2: Verify Docker Installation

Run the verification script:

```bash
./verify_docker.sh
```

This will check:
- ✅ Docker is installed
- ✅ Docker daemon is running
- ✅ Docker is working correctly
- ✅ Model file exists
- ✅ Docker configuration files are present

**Expected Output:**
```
==========================================
Docker Installation Verification
==========================================

1. Checking Docker installation...
   ✅ Docker is installed: Docker version 24.x.x
2. Checking Docker Compose...
   ✅ Docker Compose is installed: docker-compose version 1.x.x
3. Checking Docker daemon...
   ✅ Docker daemon is running
...
```

**If you see errors:**
- Make sure Docker Desktop is running
- Check that Docker Desktop has finished starting (no animation in menu bar)
- Wait a few seconds and try again

---

## Step 3: Train Model (If Needed)

The Docker image requires a trained model. Verify it exists:

```bash
ls -lh models/demand_model.joblib
```

**If the model doesn't exist:**
```bash
# Activate virtual environment
source venv/bin/activate

# Train the model
python train_and_evaluate_model.py
```

---

## Step 4: Build Docker Image

**Option A: Using Build Script (Recommended)**
```bash
./build_docker.sh
```

**Option B: Using Docker Command**
```bash
docker build -t fuel-price-optimizer .
```

**Expected Output:**
```
Building Docker image...
[+] Building 45.2s (15/15) FINISHED
...
✅ Docker image built successfully!

Image: fuel-price-optimizer:latest
```

**Build Time:** Typically 2-5 minutes on first build

**Troubleshooting Build:**
- If model is missing: `python train_and_evaluate_model.py`
- If Docker isn't running: Start Docker Desktop
- If build fails: Check error messages in output

---

## Step 5: Run Container

**Option A: Using Run Script (Recommended)**
```bash
./run_docker.sh
```

**Option B: Using Docker Compose**
```bash
docker-compose up -d
```

**Option C: Using Docker Command**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/outputs:/app/outputs \
  --name fuel-price-optimizer \
  --restart unless-stopped \
  fuel-price-optimizer
```

**Expected Output:**
```
Starting container...
✅ Container started successfully!

Container name: fuel-price-optimizer
API available at: http://localhost:8000

Waiting for container to be ready...
✅ API is healthy and ready!
```

---

## Step 6: Test the Container

**Option A: Using Test Script (Recommended)**
```bash
./test_container.sh
```

**Option B: Manual Testing**

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"healthy","model_loaded":true}`

2. **Root Endpoint:**
   ```bash
   curl http://localhost:8000/
   ```
   Expected: API information JSON

3. **Get Recommendation:**
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
   Expected: Recommendation with price, volume, and profit

4. **Open API Documentation:**
   ```bash
   open http://localhost:8000/docs
   ```
   Or visit in browser: http://localhost:8000/docs

---

## Common Commands

### Container Management

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs -f fuel-price-optimizer

# Stop container
docker stop fuel-price-optimizer

# Start stopped container
docker start fuel-price-optimizer

# Restart container
docker restart fuel-price-optimizer

# Remove container
docker rm fuel-price-optimizer
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi fuel-price-optimizer

# View image details
docker image inspect fuel-price-optimizer
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# View service status
docker-compose ps
```

---

## Troubleshooting

### Docker Desktop Not Starting

**Symptoms:** Docker icon animating forever or error messages

**Solutions:**
- Restart Docker Desktop
- Check system requirements
- Ensure virtualization is enabled (macOS: System Preferences → Security)
- Try restarting your computer

### Container Won't Start

**Check logs:**
```bash
docker logs fuel-price-optimizer
```

**Common Issues:**
1. **Port 8000 already in use:**
   ```bash
   lsof -i :8000  # Find what's using the port
   # Stop existing process or change port in docker-compose.yml
   ```

2. **Model not found error:**
   - Ensure model exists: `ls models/demand_model.joblib`
   - Rebuild image if model was added after build

3. **Permission errors:**
   - Check file permissions
   - Ensure outputs directory exists: `mkdir -p outputs`

### API Not Responding

**Wait for startup:**
- Container needs 5-10 seconds to start
- Check health endpoint: `curl http://localhost:8000/health`

**Check container status:**
```bash
docker ps  # Should show container as running
docker logs fuel-price-optimizer  # Check for errors
```

### Build Fails

**Common causes:**
1. **Docker not running:** Start Docker Desktop
2. **Model missing:** Train model first
3. **Network issues:** Check internet connection (needed to download base image)
4. **Out of disk space:** `docker system df` to check space

---

## Verification Checklist

After completing all steps, verify:

- [ ] Docker is installed: `docker --version`
- [ ] Docker is running: `docker info`
- [ ] Image is built: `docker images | grep fuel-price-optimizer`
- [ ] Container is running: `docker ps | grep fuel-price-optimizer`
- [ ] Health endpoint works: `curl http://localhost:8000/health`
- [ ] Recommendation endpoint works: `curl -X POST http://localhost:8000/recommend ...`
- [ ] API docs accessible: Open http://localhost:8000/docs

---

## Next Steps

Once everything is working:

1. **Integrate with your application:**
   - Use the API endpoint in your code
   - Set up API keys if needed (not currently implemented)

2. **Deploy to production:**
   - See `DOCKER_README.md` for production deployment
   - Set up reverse proxy (nginx, traefik)
   - Configure SSL/HTTPS
   - Set up monitoring

3. **CI/CD Integration:**
   - Build and push images to registry
   - Automate deployment
   - Set up health checks

---

## Quick Reference

| Task | Command |
|------|---------|
| Verify Docker | `./verify_docker.sh` |
| Build image | `./build_docker.sh` |
| Run container | `./run_docker.sh` |
| Test API | `./test_container.sh` |
| View logs | `docker logs -f fuel-price-optimizer` |
| Stop container | `docker stop fuel-price-optimizer` |
| Start container | `docker start fuel-price-optimizer` |
| Remove container | `docker rm fuel-price-optimizer` |

---

## Getting Help

- **Docker issues:** Check `INSTALL_DOCKER.md`
- **Deployment:** Check `DOCKER_README.md`
- **API usage:** Check `PROJECT_SUMMARY.md`
- **General setup:** Check `STEPS_TO_RUN.md`

---

**Congratulations!** Your Fuel Price Optimizer is now containerized and ready to use! 🎉

