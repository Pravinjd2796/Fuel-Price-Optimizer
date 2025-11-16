# Batch Scheduling Configuration

This directory contains configurations for running daily price recommendations on a schedule using various schedulers.

## Available Scheduling Options

### 1. **Cron (Simple & Built-in)** ✅ Recommended for Production Servers
- **File**: `cron_example.txt`
- **Pros**: Built into Unix/Linux, lightweight, reliable
- **Cons**: No GUI, requires server access
- **Best for**: Production servers, simple deployments

### 2. **APScheduler (Python-based)** ✅ Recommended for Development
- **File**: `apscheduler_example.py`
- **Pros**: Simple Python library, easy to integrate, no external services
- **Cons**: Requires Python process to run continuously
- **Best for**: Development, simple deployments, testing

### 3. **Prefect (Modern Workflow Orchestration)** ✅ Recommended for Complex Workflows
- **File**: `prefect_flow.py`
- **Pros**: Modern, feature-rich, great UI, easy testing
- **Cons**: Requires Prefect server/cloud
- **Best for**: Production with complex workflows, monitoring needs

### 4. **Apache Airflow (Enterprise Grade)** ✅ Recommended for Large Scale
- **File**: `airflow_dag.py`
- **Pros**: Very powerful, great for complex dependencies, mature ecosystem
- **Cons**: Heavyweight, requires Airflow server setup
- **Best for**: Enterprise deployments, complex data pipelines

---

## Quick Start Guide

### Option 1: Cron (Simplest)

1. **Create logs directory:**
   ```bash
   mkdir -p logs
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add cron job (adjust paths):**
   ```
   0 6 * * * cd "/Users/pravinjadhav/Desktop/Pravin/fuel price optimizer" && /usr/bin/python3 src/batch_job.py >> logs/cron.log 2>&1
   ```

4. **Save and exit**

5. **Verify:**
   ```bash
   crontab -l
   ```

**Test manually first:**
```bash
cd "/Users/pravinjadhav/Desktop/Pravin/fuel price optimizer"
python src/batch_job.py
```

---

### Option 2: APScheduler (Python-based)

1. **Install APScheduler:**
   ```bash
   pip install apscheduler
   ```

2. **Run scheduler:**
   ```bash
   python scheduling/apscheduler_example.py
   ```

3. **The scheduler will run in the foreground. Press Ctrl+C to stop.**

**Run in background (Linux/macOS):**
```bash
nohup python scheduling/apscheduler_example.py > logs/scheduler.log 2>&1 &
```

**Run as systemd service (Linux):**
Create `/etc/systemd/system/fuel-price-scheduler.service`:
```ini
[Unit]
Description=Fuel Price Optimizer Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/fuel price optimizer
ExecStart=/path/to/python scheduling/apscheduler_example.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable fuel-price-scheduler
sudo systemctl start fuel-price-scheduler
sudo systemctl status fuel-price-scheduler
```

---

### Option 3: Prefect (Modern Workflow)

1. **Install Prefect:**
   ```bash
   pip install prefect
   ```

2. **Start Prefect server (optional, for UI):**
   ```bash
   prefect server start
   ```
   Access UI at: http://localhost:4200

3. **Run flow manually:**
   ```bash
   python scheduling/prefect_flow.py
   ```

4. **Create deployment with schedule:**
   ```bash
   prefect deployment build scheduling/prefect_flow.py:price_recommendation_flow \
     -n daily-recommendations \
     --cron "0 6 * * *"
   
   prefect deployment apply price_recommendation_flow-deployment.yaml
   ```

5. **Run deployment:**
   ```bash
   prefect deployment run price_recommendation_flow/daily-recommendations
   ```

**Using Prefect Cloud:**
```bash
prefect cloud login
prefect deployment apply price_recommendation_flow-deployment.yaml
```

---

### Option 4: Apache Airflow

1. **Install Airflow:**
   ```bash
   pip install apache-airflow
   export AIRFLOW_HOME=/path/to/airflow_home
   ```

2. **Initialize Airflow:**
   ```bash
   airflow db init
   airflow users create \
     --username admin \
     --password admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com
   ```

3. **Copy DAG file:**
   ```bash
   cp scheduling/airflow_dag.py $AIRFLOW_HOME/dags/price_recommendation_dag.py
   ```

4. **Start Airflow:**
   ```bash
   # Terminal 1: Start webserver
   airflow webserver --port 8080
   
   # Terminal 2: Start scheduler
   airflow scheduler
   ```

5. **Access UI:**
   Open http://localhost:8080 (login: admin/admin)

6. **Enable DAG in UI:**
   - Find `daily_price_recommendation` DAG
   - Toggle it ON
   - It will run daily at 6:00 AM

---

## Batch Job Script

All schedulers use `src/batch_job.py` which:

- ✅ Fetches today's market data
- ✅ Loads the trained model
- ✅ Generates price recommendation
- ✅ Applies business guardrails
- ✅ Saves recommendation to `outputs/recommendation_YYYY-MM-DD.json`
- ✅ Handles errors gracefully
- ✅ Provides detailed logging

**Manual execution:**
```bash
# Run for today
python src/batch_job.py

# Run for specific date
python src/batch_job.py --date 2024-12-31

# Use custom guardrails
python src/batch_job.py --guardrails-json config/guardrails.json
```

---

## Configuration

### Schedule Times

All schedulers are configured to run **daily at 6:00 AM**. To change:

- **Cron**: Edit the cron expression in `cron_example.txt`
- **APScheduler**: Edit `CronTrigger(hour=6, minute=0)` in `apscheduler_example.py`
- **Prefect**: Edit `CronSchedule(cron="0 6 * * *")` in `prefect_flow.py`
- **Airflow**: Edit `schedule_interval='0 6 * * *'` in `airflow_dag.py`

### Guardrails Configuration

Create `config/guardrails.json`:
```json
{
  "max_change_pct": 0.03,
  "min_margin": 1.0,
  "min_price": 20.0,
  "max_price": 1000.0,
  "max_vs_comp_pct": 0.10
}
```

Use with batch job:
```bash
python src/batch_job.py --guardrails-json config/guardrails.json
```

---

## Monitoring & Logs

### Cron Logs
```bash
tail -f logs/cron.log
```

### APScheduler Logs
```bash
tail -f logs/scheduler.log
```

### Prefect UI
- Access at http://localhost:4200 (if running Prefect server)
- View flow runs, logs, and metrics

### Airflow UI
- Access at http://localhost:8080
- View DAG runs, task logs, and graphs

---

## Comparison Table

| Feature | Cron | APScheduler | Prefect | Airflow |
|---------|------|-------------|---------|---------|
| **Setup Complexity** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ Complex |
| **GUI** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Monitoring** | ⭐ Basic | ⭐ Basic | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Excellent |
| **Dependencies** | ⭐ None | ⭐⭐ Python | ⭐⭐⭐ Server | ⭐⭐⭐⭐ Heavy |
| **Best For** | Production | Development | Modern Workflows | Enterprise |
| **Learning Curve** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ Steep |

---

## Recommendation

- **Development/Testing**: Use **APScheduler** (simple, easy to test)
- **Production (Simple)**: Use **Cron** (reliable, lightweight)
- **Production (Complex)**: Use **Prefect** (modern, good monitoring)
- **Enterprise (Large Scale)**: Use **Airflow** (powerful, mature)

---

## Troubleshooting

### Batch Job Fails

1. **Check model exists:**
   ```bash
   ls -lh models/demand_model.joblib
   ```

2. **Test manually:**
   ```bash
   python src/batch_job.py
   ```

3. **Check logs:**
   ```bash
   cat logs/cron.log  # or scheduler.log
   ```

### Scheduler Not Running

1. **Verify schedule configuration**
2. **Check system time/timezone**
3. **Verify Python path in scheduler config**
4. **Check file permissions**

### Prefect/Airflow Issues

1. **Check server is running**
2. **Verify database is initialized**
3. **Check DAG/Flow files are in correct location**
4. **Review logs in UI**

---

## Next Steps

1. Choose a scheduling option based on your needs
2. Configure the schedule time
3. Set up monitoring/logging
4. Test with manual runs first
5. Enable in production

For questions or issues, refer to:
- Batch job: `src/batch_job.py`
- API: `src/api.py`
- Main docs: `PROJECT_SUMMARY.md`

