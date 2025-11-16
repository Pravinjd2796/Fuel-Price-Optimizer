# Fuel Price Optimizer

[![CI](https://github.com/username/fuel-price-optimizer/workflows/CI/badge.svg)](https://github.com/username/fuel-price-optimizer/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A machine learning-powered fuel price optimization system that recommends optimal daily retail prices to maximize profit while respecting business guardrails and market conditions.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Batch Scheduling](#batch-scheduling)
- [Project Structure](#project-structure)
- [Model Performance](#model-performance)
- [CI/CD Pipeline](#cicd-pipeline)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The Fuel Price Optimizer is an end-to-end ML system designed for retail petrol companies operating in competitive markets. It uses historical data and daily market inputs to recommend optimal pricing strategies that maximize daily profit.

### Key Capabilities

- **ML-Powered Demand Prediction**: XGBoost model trained on historical data
- **Price Optimization**: Grid search algorithm to find profit-maximizing prices
- **Business Guardrails**: Configurable constraints (price change limits, margins, competitiveness)
- **REST API**: FastAPI-based service for easy integration
- **Batch Processing**: Automated daily recommendations via schedulers
- **Docker Support**: Containerized deployment ready
- **CI/CD Ready**: Automated testing and deployment pipelines

---

## ✨ Features

### Core Features
- ✅ **Demand Forecasting**: Predicts sales volume based on price and market conditions
- ✅ **Profit Optimization**: Maximizes daily profit (price - cost) × predicted_volume
- ✅ **Business Rules**: Enforces guardrails (max price change, min margin, competitive constraints)
- ✅ **Feature Engineering**: 16 engineered features including temporal, price, and competitor features
- ✅ **Model Evaluation**: Comprehensive validation with cross-validation

### Technical Features
- ✅ **REST API**: FastAPI with Swagger UI documentation
- ✅ **Batch Jobs**: Automated daily recommendation generation
- ✅ **Docker Support**: Multi-stage builds, optimized images
- ✅ **Scheduling**: Support for Cron, APScheduler, Prefect, and Airflow
- ✅ **CI/CD**: GitHub Actions and GitLab CI configurations
- ✅ **Testing**: Unit tests with coverage reporting
- ✅ **Code Quality**: Linting, formatting, and type checking

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- (Optional) Docker for containerized deployment

### 5-Minute Setup

```bash
# 1. Clone or navigate to project
cd "fuel price optimizer"

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the model
python train_and_evaluate_model.py

# 5. Run example recommendation
python run_example.py

# 6. Start API server
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Access API docs:** http://localhost:8000/docs

---

## 📦 Installation

### Standard Installation

```bash
# Install base requirements
pip install -r requirements.txt

# For development (includes testing and code quality tools)
pip install -r requirements-dev.txt
```

### Optional: Scheduling Dependencies

Choose based on your needs:

```bash
# APScheduler (simple Python-based)
pip install apscheduler

# Prefect (modern workflow orchestration)
pip install prefect

# Apache Airflow (enterprise-grade)
pip install apache-airflow
```

See [requirements.txt](requirements.txt) for complete dependency list.

---

## 💻 Usage

### 1. Train the Model

```bash
# Full training with comprehensive evaluation
python train_and_evaluate_model.py

# Simple training (faster)
python train_and_save_model.py
```

**Output:** Model saved to `models/demand_model.joblib`

### 2. Get Price Recommendation (CLI)

```bash
# Simple example
python run_example.py

# Batch job (for schedulers)
python src/batch_job.py

# With custom date
python src/batch_job.py --date 2024-12-31

# With custom guardrails
python src/batch_job.py --guardrails-json config/guardrails.json
```

**Output:** Recommendation saved to `outputs/recommendation_YYYY-MM-DD.json`

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html
```

### 4. Start API Server

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Endpoints:**
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📡 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

#### `POST /recommend`
Get price recommendation.

**Request:**
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

**Response:**
```json
{
  "date": "2024-12-31",
  "recommended_price": 97.14,
  "expected_volume": 14284.52,
  "expected_profit": 162441.10,
  "guardrail_applied": false,
  "violation_reason": null,
  "candidates_tried": 41
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example: Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get recommendation
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

---

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build image
./build_docker.sh
# or
docker build -t fuel-price-optimizer .

# Run container
./run_docker.sh
# or
docker-compose up -d

# Test container
./test_container.sh
```

### Verify Docker Installation

```bash
./verify_docker.sh
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**For detailed Docker setup, see:**
- [DOCKER_README.md](DOCKER_README.md) - Docker deployment guide
- [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) - Complete setup guide
- [INSTALL_DOCKER.md](INSTALL_DOCKER.md) - Docker installation

---

## ⏰ Batch Scheduling

Automate daily price recommendations using schedulers.

### Option 1: Cron (Simple)

```bash
# Edit crontab
crontab -e

# Add line (adjust paths)
0 6 * * * cd "/path/to/fuel price optimizer" && python src/batch_job.py >> logs/cron.log 2>&1
```

### Option 2: APScheduler (Python-based)

```bash
pip install apscheduler
python scheduling/apscheduler_example.py
```

### Option 3: Prefect (Modern Workflow)

```bash
pip install prefect
prefect server start
python scheduling/prefect_flow.py
```

### Option 4: Apache Airflow (Enterprise)

```bash
pip install apache-airflow
airflow db init
cp scheduling/airflow_dag.py $AIRFLOW_HOME/dags/
airflow webserver --port 8080  # Terminal 1
airflow scheduler              # Terminal 2
```

**For detailed scheduling guide, see:** [scheduling/SCHEDULING_README.md](scheduling/SCHEDULING_README.md)

---

## 📁 Project Structure

```
fuel price optimizer/
├── .github/
│   └── workflows/
│       ├── ci.yml                      # CI/CD pipeline
│       └── model-training.yml          # Model training pipeline
├── config/
│   └── guardrails.json                 # Business guardrails configuration
├── data/
│   ├── oil_retail_history.csv          # Historical training data
│   └── today_example.json              # Example daily input
├── models/
│   └── demand_model.joblib             # Trained ML model
├── outputs/                            # Generated recommendations
├── scheduling/
│   ├── airflow_dag.py                  # Airflow DAG
│   ├── apscheduler_example.py          # APScheduler example
│   ├── prefect_flow.py                 # Prefect workflow
│   ├── cron_example.txt                # Cron examples
│   ├── SCHEDULING_README.md            # Scheduling guide
│   └── AIRFLOW_EXPLAINED.md            # Airflow concepts
├── src/
│   ├── api.py                          # FastAPI server
│   ├── batch_job.py                    # Batch job script
│   ├── data_pipeline.py                # Data processing
│   ├── models.py                       # ML model functions
│   ├── optimizer.py                    # Price optimization
│   ├── features.py                     # Feature engineering
│   └── utils.py                        # Utilities
├── tests/
│   └── test_pipeline.py                # Unit tests
├── notebook/                           # Jupyter notebooks
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Docker Compose config
├── requirements.txt                    # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── train_and_evaluate_model.py        # Model training script
├── run_example.py                      # Example runner
└── README.md                           # This file
```

---

## 📊 Model Performance

### Test Set Performance

- **RMSE**: 732.85 liters
- **MAE**: 551.24 liters
- **R²**: 0.3274
- **MAPE**: 3.97%
- **RMSE/Mean**: 5.27%

### Cross-Validation (5-fold Time Series Split)

- **Average RMSE**: 787.42 (±39.62) liters
- **Average R²**: 0.23 (±0.15)
- **Average MAPE**: 4.40% (±0.34%)

### Feature Importance (Top 5)

1. `dayofweek` (56.14%) - Day of week
2. `margin` (4.87%) - Profit margin
3. `margin_pct` (4.18%) - Margin percentage
4. `price_diff` (3.77%) - Price differential
5. `vol_lag1` (3.56%) - Previous day's volume

**For detailed model information, see:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🔄 CI/CD Pipeline

The project includes complete CI/CD configurations:

### GitHub Actions

- **Workflow**: `.github/workflows/ci.yml`
- **Features**: Automated testing, linting, Docker builds, deployment
- **Status**: Ready to use

### GitLab CI

- **Configuration**: `.gitlab-ci.yml`
- **Features**: Test, lint, build, deploy stages
- **Status**: Ready to use

### Pipeline Stages

1. **Test**: Run unit tests with coverage
2. **Lint**: Code quality checks (black, flake8, mypy)
3. **Build**: Docker image build and test
4. **Deploy**: Staging and production deployment

**For CI/CD setup, see:** [CI_CD_README.md](CI_CD_README.md)

---

## 📚 Documentation

### Main Documentation

- **[STEPS_TO_RUN.md](STEPS_TO_RUN.md)** - Complete step-by-step guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Comprehensive project documentation
- **[CI_CD_README.md](CI_CD_README.md)** - CI/CD setup guide
- **[CI_CD_ASSESSMENT.md](CI_CD_ASSESSMENT.md)** - CI/CD readiness assessment

### Docker Documentation

- **[DOCKER_README.md](DOCKER_README.md)** - Docker deployment guide
- **[DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md)** - Complete Docker setup
- **[INSTALL_DOCKER.md](INSTALL_DOCKER.md)** - Docker installation instructions

### Scheduling Documentation

- **[scheduling/SCHEDULING_README.md](scheduling/SCHEDULING_README.md)** - Scheduling guide
- **[scheduling/AIRFLOW_EXPLAINED.md](scheduling/AIRFLOW_EXPLAINED.md)** - Airflow concepts

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/ --ignore-missing-imports

# Sort imports
isort src/ tests/
```

---

## 🔧 Configuration

### Guardrails Configuration

Edit `config/guardrails.json`:

```json
{
  "max_change_pct": 0.03,
  "min_margin": 1.0,
  "min_price": 20.0,
  "max_price": 1000.0,
  "max_vs_comp_pct": 0.10
}
```

### Environment Variables

Create `.env` file (optional):

```bash
API_PORT=8000
LOG_LEVEL=info
MODEL_PATH=models/demand_model.joblib
```

---

## 🐛 Troubleshooting

### Common Issues

**Model not found:**
```bash
python train_and_evaluate_model.py
```

**Port 8000 already in use:**
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
```

**Docker not found:**
- See [INSTALL_DOCKER.md](INSTALL_DOCKER.md) for installation

**Import errors:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**For more troubleshooting, see:** [STEPS_TO_RUN.md](STEPS_TO_RUN.md#troubleshooting)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Run linting (`black src/ tests/` and `flake8 src/ tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks (if configured)
pre-commit install
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- ML powered by [XGBoost](https://xgboost.readthedocs.io/)
- Data processing with [Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/)

---

## 📞 Support

For questions, issues, or contributions:

- **Issues**: Open an issue on GitHub
- **Documentation**: See [STEPS_TO_RUN.md](STEPS_TO_RUN.md) for detailed guides
- **Email**: [Your email here]

---

## 🗺️ Roadmap

- [ ] Model retraining automation
- [ ] Real-time price updates
- [ ] Multi-product support
- [ ] Advanced guardrails (ML-based)
- [ ] Dashboard for monitoring
- [ ] A/B testing framework

---

## 📈 Status

**Project Status**: ✅ Production Ready

- ✅ Core functionality complete
- ✅ API implemented
- ✅ Docker support
- ✅ CI/CD configured
- ✅ Documentation complete
- ✅ Tests passing

---

**Made with ❤️ for fuel price optimization**

---

## Quick Links

- [Quick Start Guide](STEPS_TO_RUN.md#quick-start)
- [API Documentation](http://localhost:8000/docs) (when server is running)
- [Docker Setup](DOCKER_SETUP_GUIDE.md)
- [Scheduling Guide](scheduling/SCHEDULING_README.md)
- [CI/CD Setup](CI_CD_README.md)

