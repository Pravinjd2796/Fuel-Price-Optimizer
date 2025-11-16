# Fuel Price Optimizer - Complete Step-by-Step Run Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Model Training](#model-training)
4. [Running Recommendations](#running-recommendations)
5. [API Server](#api-server)
6. [Docker Deployment](#docker-deployment)
7. [Batch Scheduling](#batch-scheduling)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.8+ installed
- Terminal/Command line access
- (Optional) Docker installed (for containerization)
- (Optional) Git (for version control and CI/CD)

---

## Initial Setup

### Step 1: Navigate to Project Directory

```bash
cd "/Users/pravinjadhav/Desktop/Pravin/fuel price optimizer"
```

### Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

**Note:** If virtual environment doesn't exist, create one:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Optional scheduling dependencies** (install as needed):
```bash
# For APScheduler
pip install apscheduler

# For Prefect
pip install prefect

# For Airflow
pip install apache-airflow
```

---

## Model Training

### Step 4: Train the Model (Required First Time)

Train the model with comprehensive evaluation:

```bash
python train_and_evaluate_model.py
```

**This will:**
- Load historical data from `data/oil_retail_history.csv`
- Clean and process the data
- Train XGBoost model
- Evaluate performance (Train/Val/Test splits + Cross-validation)
- Show feature importance
- Save model to `models/demand_model.joblib`

**Expected output:** Model performance metrics, validation results, and feature importance

**Alternative - Simple Training:**
```bash
python train_and_save_model.py
```

---

## Running Recommendations

### Step 5: Run Price Recommendation (CLI - Simple)

Get a price recommendation using the example data:

```bash
python run_example.py
```

**This will:**
- Load today's data from `data/today_example.json`
- Use trained model to predict demand
- Optimize price to maximize profit
- Apply business guardrails
- Save recommendation to `outputs/recommendation_YYYY-MM-DD.json`

**Expected output:** Recommended price, expected volume, expected profit, and guardrail status

### Step 6: Run Batch Job (Advanced)

Run daily price recommendation as a batch job:

```bash
# Run for today
python src/batch_job.py

# Run for specific date
python src/batch_job.py --date 2024-12-31

# Use custom guardrails
python src/batch_job.py --guardrails-json config/guardrails.json

# Specify output directory
python src/batch_job.py --output-dir outputs/
```

**This is the script used by schedulers (Cron, Airflow, Prefect, etc.)**

---

## API Server

### Step 7: Start API Server (FastAPI)

Start the FastAPI server:

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Server will start on:** `http://localhost:8000`

**Keep this terminal open** - the server runs in the foreground.

### Step 8: Test API Endpoints

#### Option A: Using curl

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Get Price Recommendation:**
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

#### Option B: Using Postman

1. **Open Postman**
2. **Health Check:**
   - Method: `GET`
   - URL: `http://localhost:8000/health`
   - Send request

3. **Get Recommendation:**
   - Method: `POST`
   - URL: `http://localhost:8000/recommend`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "date": "2024-12-31",
     "cost": 85.77,
     "comp1_price": 95.01,
     "comp2_price": 95.7,
     "comp3_price": 95.21,
     "last_price": 94.45
   }
   ```

4. **Interactive API Docs:**
   - Open browser: `http://localhost:8000/docs`
   - Test endpoints directly in Swagger UI

#### Option C: Using Browser

- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

---

## Docker Deployment

### Prerequisites for Docker

1. **Install Docker Desktop** (see `INSTALL_DOCKER.md` for details)

2. **Verify Docker Installation:**
   ```bash
   ./verify_docker.sh
   ```

### Step 9: Build Docker Image

#### Option A: Using Build Script (Recommended)
```bash
./build_docker.sh
```

#### Option B: Using Docker Command
```bash
docker build -t fuel-price-optimizer .
```

### Step 10: Run Docker Container

#### Option A: Using Run Script (Recommended)
```bash
./run_docker.sh
```

#### Option B: Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

#### Option C: Using Docker Command
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/outputs:/app/outputs \
  --name fuel-price-optimizer \
  --restart unless-stopped \
  fuel-price-optimizer
```

### Step 11: Test Docker Container

```bash
# Test using script
./test_container.sh

# Or test manually
curl http://localhost:8000/health
```

**View logs:**
```bash
docker logs -f fuel-price-optimizer
```

**Stop container:**
```bash
docker stop fuel-price-optimizer
docker rm fuel-price-optimizer

# Or with docker-compose
docker-compose down
```

**For detailed Docker setup, see:**
- `DOCKER_README.md` - Docker deployment guide
- `DOCKER_SETUP_GUIDE.md` - Complete Docker setup guide

---

## Batch Scheduling

Automate daily price recommendations using schedulers.

### Step 12: Choose a Scheduler

#### Option 1: Cron (Simple - Recommended for Production Servers)

1. **Create logs directory:**
   ```bash
   mkdir -p logs
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add cron job** (adjust paths):
   ```
   0 6 * * * cd "/path/to/fuel price optimizer" && /usr/bin/python3 src/batch_job.py >> logs/cron.log 2>&1
   ```

4. **See `scheduling/cron_example.txt`** for more examples

**Documentation:** See `scheduling/SCHEDULING_README.md`

#### Option 2: APScheduler (Python-based - Recommended for Development)

1. **Install APScheduler:**
   ```bash
   pip install apscheduler
   ```

2. **Run scheduler:**
   ```bash
   python scheduling/apscheduler_example.py
   ```

**Documentation:** See `scheduling/SCHEDULING_README.md`

#### Option 3: Prefect (Modern Workflow - Recommended for Complex Workflows)

1. **Install Prefect:**
   ```bash
   pip install prefect
   ```

2. **Start Prefect server (optional):**
   ```bash
   prefect server start
   ```

3. **Run flow:**
   ```bash
   python scheduling/prefect_flow.py
   ```

**Documentation:** See `scheduling/SCHEDULING_README.md`

#### Option 4: Apache Airflow (Enterprise Grade - Recommended for Large Scale)

1. **Install Airflow:**
   ```bash
   pip install apache-airflow
   export AIRFLOW_HOME=/path/to/airflow_home
   ```

2. **Initialize Airflow:**
   ```bash
   airflow db init
   airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
   ```

3. **Copy DAG file:**
   ```bash
   cp scheduling/airflow_dag.py $AIRFLOW_HOME/dags/price_recommendation_dag.py
   ```

4. **Start Airflow:**
   ```bash
   # Terminal 1: Web server
   airflow webserver --port 8080
   
   # Terminal 2: Scheduler
   airflow scheduler
   ```

5. **Access UI:** `http://localhost:8080` (admin/admin)

**Documentation:** 
- `scheduling/SCHEDULING_README.md` - Scheduling guide
- `scheduling/AIRFLOW_EXPLAINED.md` - Airflow concepts explained

---

## CI/CD Pipeline

### Step 13: Enable CI/CD (Optional but Recommended)

Your project is **100% ready for CI/CD**! (See `CI_CD_ASSESSMENT.md`)

#### For GitHub:

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **GitHub Actions will run automatically:**
   - Go to **Actions** tab in GitHub
   - View pipeline runs and status

**Workflows:**
- `.github/workflows/ci.yml` - Main CI/CD pipeline
- `.github/workflows/model-training.yml` - Model training pipeline

#### For GitLab:

1. **Push code to GitLab:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **GitLab CI will run automatically:**
   - Go to **CI/CD → Pipelines** in GitLab
   - View pipeline runs and status

**Configuration:** `.gitlab-ci.yml`

**Documentation:** 
- `CI_CD_README.md` - Complete CI/CD setup guide
- `CI_CD_ASSESSMENT.md` - Readiness assessment

---

## Testing

### Step 14: Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Expected output:** All tests should pass ✓

### Step 15: Code Quality Checks

```bash
# Install development dependencies
pip install black flake8 mypy isort

# Check code formatting
black --check src/ tests/

# Run linter
flake8 src/ tests/

# Check imports
isort --check-only src/ tests/

# Type checking
mypy src/ --ignore-missing-imports
```

---

## Quick Reference Commands

### Model Training
```bash
python train_and_evaluate_model.py      # Full evaluation
python train_and_save_model.py          # Simple training
```

### Running Recommendations
```bash
python run_example.py                   # Simple CLI example
python src/batch_job.py                 # Batch job script
python src/batch_job.py --date 2024-12-31  # Specific date
```

### API Server
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000  # Start server
# Press Ctrl+C to stop
```

### Docker
```bash
./build_docker.sh                       # Build image
./run_docker.sh                         # Run container
./test_container.sh                     # Test container
docker-compose up -d                    # Using compose
docker-compose down                     # Stop with compose
```

### Testing
```bash
pytest tests/ -v                        # Run tests
pytest tests/ -v --cov=src              # With coverage
```

### Scheduling
```bash
python scheduling/apscheduler_example.py  # APScheduler
python scheduling/prefect_flow.py         # Prefect
# See scheduling/SCHEDULING_README.md for Cron and Airflow
```

---

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Model not found
**Solution:** Train the model first:
```bash
python train_and_evaluate_model.py
```

### Issue: Port 8000 already in use
**Solution:** Use a different port:
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
```

### Issue: Docker not found
**Solution:** Install Docker Desktop:
- macOS: `brew install --cask docker` or download from docker.com
- See `INSTALL_DOCKER.md` for detailed instructions

### Issue: Docker build fails
**Solution:** 
1. Check if model exists: `ls models/demand_model.joblib`
2. Train model if missing: `python train_and_evaluate_model.py`
3. Check Docker is running: `docker info`

### Issue: Scheduler not running
**Solution:**
1. Check schedule configuration
2. Verify Python path in scheduler config
3. Check file permissions
4. Review logs: `tail -f logs/cron.log` (for Cron)

### Issue: CI/CD pipeline fails
**Solution:**
1. Run tests locally: `pytest tests/ -v`
2. Check linting locally: `flake8 src/ tests/`
3. Build Docker locally: `docker build -t fuel-price-optimizer .`
4. Check logs in CI/CD UI (GitHub Actions or GitLab CI)

### Issue: Permission denied
**Solution:** Check file permissions and ensure you're in the correct directory

---

## Project Structure

```
fuel price optimizer/
├── .github/
│   └── workflows/
│       ├── ci.yml                      # CI/CD pipeline
│       └── model-training.yml          # Model training pipeline
├── config/
│   └── guardrails.json                 # Guardrails configuration
├── data/
│   ├── oil_retail_history.csv          # Historical training data
│   └── today_example.json              # Example input for recommendations
├── models/
│   └── demand_model.joblib             # Trained model (created after training)
├── outputs/
│   └── recommendation_*.json           # Generated recommendations
├── scheduling/
│   ├── airflow_dag.py                  # Airflow DAG configuration
│   ├── apscheduler_example.py          # APScheduler example
│   ├── prefect_flow.py                 # Prefect workflow
│   ├── cron_example.txt                # Cron configuration examples
│   ├── SCHEDULING_README.md            # Scheduling guide
│   └── AIRFLOW_EXPLAINED.md            # Airflow concepts
├── src/
│   ├── api.py                          # FastAPI server
│   ├── batch_job.py                    # Batch job script
│   ├── data_pipeline.py                # Data processing
│   ├── models.py                       # ML model functions
│   ├── optimizer.py                    # Price optimization logic
│   ├── features.py                     # Feature engineering
│   └── utils.py                        # Utilities
├── tests/
│   └── test_pipeline.py                # Unit tests
├── notebook/                           # Jupyter notebooks for exploration
├── .dockerignore                       # Docker ignore file
├── .gitignore                          # Git ignore file
├── .gitlab-ci.yml                      # GitLab CI configuration
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Docker Compose configuration
├── build_docker.sh                     # Docker build script
├── run_docker.sh                       # Docker run script
├── test_container.sh                   # Docker test script
├── verify_docker.sh                    # Docker verification script
├── requirements.txt                    # Python dependencies
├── train_and_evaluate_model.py        # Full training with validation
├── train_and_save_model.py            # Simple training script
├── run_example.py                      # CLI for recommendations
├── STEPS_TO_RUN.md                     # This file
├── PROJECT_SUMMARY.md                  # Project summary
├── DOCKER_README.md                    # Docker deployment guide
├── DOCKER_SETUP_GUIDE.md               # Docker setup guide
├── INSTALL_DOCKER.md                   # Docker installation guide
├── CI_CD_README.md                     # CI/CD setup guide
└── CI_CD_ASSESSMENT.md                 # CI/CD readiness assessment
```

---

## Expected Outputs

### After Training:
- Model saved at: `models/demand_model.joblib`
- Console output with performance metrics
- Cross-validation results

### After Running Example/Batch Job:
- Recommendation file: `outputs/recommendation_YYYY-MM-DD.json`
- Console output with recommended price and profit
- Logs (if using scheduler): `logs/cron.log` or similar

### After API Request:
- JSON response with:
  - `recommended_price`
  - `expected_volume`
  - `expected_profit`
  - `guardrail_applied`
  - `violation_reason`

---

## Documentation Reference

### Getting Started
- **This File**: `STEPS_TO_RUN.md` - Complete run guide
- **Project Summary**: `PROJECT_SUMMARY.md` - Full project documentation

### Docker
- **Docker Guide**: `DOCKER_README.md` - Docker deployment
- **Setup Guide**: `DOCKER_SETUP_GUIDE.md` - Complete Docker setup
- **Install Guide**: `INSTALL_DOCKER.md` - Docker installation

### Scheduling
- **Scheduling Guide**: `scheduling/SCHEDULING_README.md` - All schedulers
- **Airflow Explained**: `scheduling/AIRFLOW_EXPLAINED.md` - Airflow concepts

### CI/CD
- **CI/CD Guide**: `CI_CD_README.md` - CI/CD setup
- **Assessment**: `CI_CD_ASSESSMENT.md` - Readiness check

---

## Next Steps

1. ✅ **Initial Setup** - Complete steps 1-3
2. ✅ **Train Model** - Complete step 4
3. ✅ **Run Recommendations** - Complete steps 5-6
4. ✅ **Start API** - Complete steps 7-8
5. ✅ **Docker Deployment** - Complete steps 9-11 (optional)
6. ✅ **Batch Scheduling** - Complete step 12 (optional)
7. ✅ **CI/CD Pipeline** - Complete step 13 (optional)
8. ✅ **Testing** - Complete steps 14-15

---

**Your project is production-ready! 🚀**

For questions or issues, refer to the troubleshooting section or relevant documentation files.
