# CI/CD Pipeline Documentation

This document describes the CI/CD pipeline setup for the Fuel Price Optimizer project.

## CI/CD Status

✅ **The project is ready for CI/CD pipeline!**

### What's Already Configured:

1. ✅ **Tests**: Unit tests in `tests/`
2. ✅ **Docker**: Dockerfile and docker-compose.yml
3. ✅ **Build Scripts**: Automated build scripts
4. ✅ **Requirements**: Properly defined dependencies
5. ✅ **Documentation**: Comprehensive docs

### What's Been Added:

1. ✅ **GitHub Actions**: `.github/workflows/ci.yml`
2. ✅ **GitLab CI**: `.gitlab-ci.yml`
3. ✅ **Model Training Pipeline**: `.github/workflows/model-training.yml`
4. ✅ **Git Ignore**: `.gitignore`

---

## CI/CD Pipeline Overview

### Pipeline Stages

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Test   │ → │  Lint   │ → │  Build  │ → │ Deploy  │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

### 1. **Test Stage**
- Run unit tests with pytest
- Generate coverage reports
- Upload coverage to Codecov

### 2. **Lint Stage**
- Code formatting check (black)
- Linting (flake8)
- Import sorting (isort)
- Type checking (mypy)

### 3. **Build Stage**
- Build Docker image
- Test Docker image
- Cache Docker layers

### 4. **Deploy Stage**
- Deploy to staging (develop branch)
- Deploy to production (main branch)

---

## GitHub Actions

### Setup

1. **Enable GitHub Actions** in your repository settings

2. **Secrets** (optional, for deployments):
   - `DOCKER_USERNAME`: Docker Hub username
   - `DOCKER_PASSWORD`: Docker Hub password
   - `GHCR_TOKEN`: GitHub Container Registry token

### Workflows

#### 1. CI/CD Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger (workflow_dispatch)

**Jobs:**
- **test**: Run tests and generate coverage
- **lint**: Code quality checks
- **build-docker**: Build and test Docker image
- **deploy-staging**: Deploy to staging (develop branch)
- **deploy-production**: Deploy to production (main branch)

**Usage:**
```bash
# Push to trigger pipeline
git push origin develop

# View status in GitHub Actions tab
```

#### 2. Model Training Pipeline (`.github/workflows/model-training.yml`)

**Triggers:**
- Scheduled: Weekly on Sunday at 2 AM UTC
- Manual trigger (workflow_dispatch)

**Jobs:**
- **train-model**: Train and evaluate model
- Upload model artifact
- Upload evaluation results

**Usage:**
```bash
# Manual trigger from GitHub Actions UI
# Or wait for scheduled run
```

---

## GitLab CI

### Setup

1. **Add `.gitlab-ci.yml`** to your repository root

2. **Configure GitLab Runner** (if self-hosted)

3. **Variables** (optional):
   - `CI_REGISTRY_USER`: GitLab registry username
   - `CI_REGISTRY_PASSWORD`: GitLab registry password

### Pipeline Stages

- **test**: Run tests with coverage
- **lint**: Code quality checks
- **build**: Build Docker image
- **deploy**: Deploy to environments

### Usage

```bash
# Push to trigger pipeline
git push origin develop

# View status in GitLab CI/CD tab
```

---

## Local CI/CD Testing

### Test Locally Before Pushing

```bash
# Run tests
pytest tests/ -v

# Run linter
flake8 src/ tests/
black --check src/ tests/

# Build Docker image
docker build -t fuel-price-optimizer:test .

# Test Docker image
docker run --rm fuel-price-optimizer:test python --version
```

### Act (GitHub Actions Locally)

Install Act: https://github.com/nektos/act

```bash
# Test GitHub Actions locally
act -l                    # List workflows
act push                  # Run push workflow
act pull_request          # Run PR workflow
```

---

## Continuous Integration Features

### ✅ Automated Testing
- Unit tests run on every push
- Test coverage reporting
- Failing tests block deployment

### ✅ Code Quality
- Linting (flake8)
- Formatting checks (black)
- Type checking (mypy)
- Import sorting (isort)

### ✅ Docker Build
- Automated Docker image builds
- Image caching for faster builds
- Multi-stage builds for optimization

### ✅ Deployment Automation
- Automatic staging deployment (develop branch)
- Manual/automatic production deployment (main branch)
- Environment-specific configurations

### ✅ Model Training
- Scheduled model retraining
- Model artifact storage
- Performance monitoring

---

## Deployment Strategies

### Option 1: Docker Compose

```yaml
# Add to CI/CD pipeline
- docker-compose -f docker-compose.staging.yml up -d
```

### Option 2: Kubernetes

```yaml
# Add to CI/CD pipeline
- kubectl apply -f k8s/staging/
- kubectl set image deployment/fuel-price-api api=$IMAGE_TAG
```

### Option 3: Cloud Services

- **AWS**: ECS, EKS, Lambda
- **Google Cloud**: Cloud Run, GKE
- **Azure**: Container Instances, AKS

---

## Environment Configuration

### Staging Environment

**Branch**: `develop`  
**Auto-deploy**: Yes  
**URL**: `http://staging.example.com`

### Production Environment

**Branch**: `main`  
**Auto-deploy**: Yes (or manual)  
**URL**: `http://production.example.com`

---

## Monitoring & Notifications

### GitHub Actions

- **Email notifications**: Configure in repository settings
- **Slack integration**: Use Slack GitHub integration
- **Status badges**: Add to README

```markdown
![CI](https://github.com/username/repo/workflows/CI/badge.svg)
```

### GitLab CI

- **Email notifications**: Configure in GitLab settings
- **Slack integration**: Use GitLab Slack integration
- **Pipeline badges**: Add to README

---

## Best Practices

### 1. **Branch Protection**
- Require status checks to pass
- Require code review
- Require up-to-date branches

### 2. **Secrets Management**
- Use CI/CD secrets, not hardcoded values
- Rotate secrets regularly
- Limit secret access

### 3. **Testing**
- Write tests for all new features
- Maintain test coverage > 80%
- Run tests locally before pushing

### 4. **Code Quality**
- Use formatters (black, isort)
- Run linters before committing
- Fix linting issues promptly

### 5. **Docker**
- Use multi-stage builds
- Cache layers effectively
- Keep images small

---

## Troubleshooting

### Tests Fail in CI

```bash
# Reproduce locally
pytest tests/ -v

# Check Python version matches CI
python --version

# Check dependencies
pip install -r requirements.txt
```

### Docker Build Fails

```bash
# Test locally
docker build -t fuel-price-optimizer:test .

# Check Dockerfile syntax
docker build --no-cache -t fuel-price-optimizer:test .
```

### Deployment Fails

```bash
# Check environment variables
echo $ENV_VAR

# Check network connectivity
ping staging.example.com

# Check logs
docker logs container-name
```

---

## Next Steps

1. **Enable GitHub Actions** or **GitLab CI** in your repository
2. **Configure secrets** for deployments (if needed)
3. **Update deployment scripts** with your actual deployment commands
4. **Set up branch protection** rules
5. **Configure notifications** (email, Slack, etc.)
6. **Add status badges** to README

---

## CI/CD Checklist

- [x] Tests configured
- [x] Linting configured
- [x] Docker build configured
- [x] GitHub Actions workflow
- [x] GitLab CI configuration
- [x] Model training pipeline
- [x] .gitignore configured
- [ ] Deployment scripts configured (update with your setup)
- [ ] Secrets configured (if needed)
- [ ] Branch protection enabled
- [ ] Notifications configured

---

## Resources

- **GitHub Actions**: https://docs.github.com/en/actions
- **GitLab CI**: https://docs.gitlab.com/ee/ci/
- **Docker**: https://docs.docker.com/
- **Pytest**: https://docs.pytest.org/
- **Black**: https://black.readthedocs.io/
- **Flake8**: https://flake8.pycqa.org/

---

**Your project is CI/CD ready! 🚀**

