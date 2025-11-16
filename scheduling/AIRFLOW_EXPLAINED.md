# Apache Airflow: DAGs and Scheduling Explained

## What is Apache Airflow?

**Apache Airflow** is an open-source platform for **programmatically authoring, scheduling, and monitoring workflows**. Think of it as a system that helps you automate and manage complex tasks that need to run at specific times or in a specific order.

### Key Concepts

#### 1. **DAG (Directed Acyclic Graph)**
- **DAG** stands for **Directed Acyclic Graph**
- It's a **blueprint** or **definition** of your workflow
- **Directed**: Tasks flow in one direction (from start to end)
- **Acyclic**: No circular dependencies (no loops)
- **Graph**: Visual representation of tasks and their relationships

#### 2. **Task**
- A single unit of work in your workflow
- Examples: "Fetch data", "Train model", "Send email"
- Tasks can depend on other tasks completing first

#### 3. **Scheduler**
- The brain of Airflow
- Constantly checks when DAGs should run
- Triggers tasks at their scheduled times
- Manages task dependencies

---

## Understanding DAGs with Examples

### Simple Example: Making Coffee

Imagine a workflow for making coffee:

```
[Heat Water] → [Brew Coffee] → [Add Milk] → [Serve]
```

This is a DAG because:
- ✅ Tasks flow in one direction (left to right)
- ✅ No circular dependencies (can't go backwards)
- ✅ Each task depends on the previous one

### Your Fuel Price Optimizer DAG

In your project (`scheduling/airflow_dag.py`), the DAG looks like:

```python
[Fetch Today's Data] → [Generate Recommendation] → [Notify Stakeholders]
     (Task 1)              (Task 2)                   (Task 3)
```

**What happens:**
1. **Task 1**: Fetches today's market data (competitor prices, costs, etc.)
2. **Task 2**: Uses the data from Task 1 to generate price recommendation
3. **Task 3**: Sends the recommendation to stakeholders (after Task 2 completes)

**Dependencies:**
- Task 2 **must wait** for Task 1 to finish
- Task 3 **must wait** for Task 2 to finish
- This ensures data flows correctly through the pipeline

---

## How Scheduling Works in Airflow

### 1. **Schedule Interval**

Defines **when** the DAG runs:

```python
schedule_interval='0 6 * * *'  # Daily at 6:00 AM
```

**Cron Expression Format:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Common Examples:**
- `'0 6 * * *'` - Daily at 6:00 AM
- `'0 */12 * * *'` - Every 12 hours
- `'0 9 * * 1-5'` - Weekdays at 9:00 AM (Mon-Fri)
- `'30 14 * * *'` - Daily at 2:30 PM
- `'0 0 1 * *'` - First day of every month at midnight

### 2. **How It Works**

```
┌─────────────────┐
│  Airflow         │
│  Scheduler       │  ← Constantly running, checking schedules
└────────┬────────┘
         │
         │ Checks: "Is it 6:00 AM?"
         │
         ▼
┌─────────────────┐
│  Time matches!  │
│  Start DAG      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute Tasks  │
│  in Order       │
└─────────────────┘
```

**Step-by-Step:**
1. **Scheduler runs 24/7** in the background
2. **Checks schedules** every few seconds
3. **When time matches** (e.g., 6:00 AM daily):
   - Creates a new "DAG Run"
   - Starts executing tasks based on dependencies
   - Monitors task execution
4. **Tracks status**: Success, Failed, Running, Skipped

---

## Visual Example: Your Fuel Price DAG

### DAG Structure

```
Daily at 6:00 AM:
┌─────────────────────┐
│ fetch_today_data    │  ← Gets market data
└──────────┬──────────┘
           │
           │ (waits for completion)
           ▼
┌─────────────────────┐
│ generate_recommend  │  ← Creates price recommendation
└──────────┬──────────┘
           │
           │ (waits for completion)
           ▼
┌─────────────────────┐
│ notify_stakeholders │  ← Sends notification
└─────────────────────┘
```

### Timeline Example

```
Day 1, 6:00 AM:
├─ [06:00:00] Scheduler triggers DAG
├─ [06:00:01] Task 1 starts: Fetch data (10 seconds)
├─ [06:00:11] Task 1 completes ✅
├─ [06:00:12] Task 2 starts: Generate recommendation (5 seconds)
├─ [06:00:17] Task 2 completes ✅
├─ [06:00:18] Task 3 starts: Notify (2 seconds)
└─ [06:00:20] Task 3 completes ✅ DAG finished!

Day 2, 6:00 AM:
├─ [06:00:00] Scheduler triggers DAG again
├─ [06:00:01] Task 1 starts...
└─ ... (same process)
```

---

## Key Features of Airflow

### 1. **Dependency Management**
Tasks automatically wait for dependencies:

```python
task_fetch_data >> task_generate_recommendation >> task_notify
# This means: fetch → generate → notify (in that order)
```

### 2. **Retry Logic**
If a task fails, Airflow can retry:

```python
default_args = {
    'retries': 2,           # Retry 2 times if task fails
    'retry_delay': timedelta(minutes=5),  # Wait 5 min between retries
}
```

### 3. **Monitoring & UI**
- **Web UI**: Visual dashboard to see DAG runs
- **Logs**: View detailed logs for each task
- **Graph View**: See DAG structure visually
- **Tree View**: See historical runs

### 4. **Backfilling**
Run DAG for past dates:

```bash
# Run DAG for last 7 days
airflow dags backfill daily_price_recommendation -s 2024-12-10 -e 2024-12-17
```

---

## Your Airflow DAG Explained

Let's break down `scheduling/airflow_dag.py`:

### 1. **DAG Definition**

```python
dag = DAG(
    'daily_price_recommendation',  # DAG name (unique identifier)
    default_args=default_args,      # Default settings for all tasks
    description='Daily fuel price recommendation job',
    schedule_interval='0 6 * * *',  # Run daily at 6:00 AM
    catchup=False,                  # Don't backfill missed runs
    tags=['price', 'optimization', 'ml'],
)
```

**What this does:**
- Creates a DAG named `daily_price_recommendation`
- Sets it to run **daily at 6:00 AM**
- Applies default settings (retries, email, etc.)

### 2. **Task Definitions**

```python
task_fetch_data = PythonOperator(
    task_id='fetch_today_data',
    python_callable=fetch_today_data,
    dag=dag,
)
```

**What this does:**
- Creates a task that runs Python function `fetch_today_data`
- Task ID: `fetch_today_data` (unique within DAG)

### 3. **Dependencies**

```python
task_fetch_data >> task_generate_recommendation >> task_notify
```

**This means:**
```
fetch_today_data → generate_recommendation → notify_stakeholders
```

**Visual:**
```
[fetch] → [generate] → [notify]
```

---

## Common Scheduling Patterns

### 1. **Daily at Fixed Time**
```python
schedule_interval='0 6 * * *'  # 6:00 AM daily
```

### 2. **Multiple Times Per Day**
```python
schedule_interval='0 */6 * * *'  # Every 6 hours
```

### 3. **Business Days Only**
```python
schedule_interval='0 9 * * 1-5'  # 9:00 AM, Mon-Fri
```

### 4. **Weekly**
```python
schedule_interval='0 0 * * 0'  # Midnight every Sunday
```

### 5. **Monthly**
```python
schedule_interval='0 0 1 * *'  # Midnight, 1st day of month
```

---

## Airflow Components

### 1. **Web Server**
- Provides UI for monitoring
- View DAGs, runs, logs
- Trigger DAGs manually
- Access: `http://localhost:8080`

### 2. **Scheduler**
- Runs in background
- Checks schedules
- Triggers DAGs
- Manages task execution

### 3. **Executor**
- Actually runs the tasks
- Can be: Sequential, Local, Celery, Kubernetes
- Your DAG uses Python functions (Local executor)

### 4. **Metadata Database**
- Stores DAG definitions
- Tracks DAG runs
- Stores task status
- Usually PostgreSQL or MySQL

---

## Advantages of Airflow

### ✅ **Benefits**

1. **Visual Workflows**: See your DAGs as graphs
2. **Dependency Management**: Automatic task ordering
3. **Retry Logic**: Handle failures gracefully
4. **Monitoring**: Track all runs in UI
5. **Scalability**: Can handle thousands of DAGs
6. **Flexibility**: Supports many task types (Python, Bash, SQL, etc.)
7. **Backfilling**: Run workflows for past dates
8. **Community**: Large ecosystem, lots of integrations

### ⚠️ **Considerations**

1. **Learning Curve**: Can be complex for simple tasks
2. **Resource Heavy**: Requires significant infrastructure
3. **Setup Time**: Takes time to set up properly
4. **Overkill**: May be too much for simple schedules

---

## When to Use Airflow

### ✅ **Good For:**

- **Complex workflows** with many dependencies
- **Enterprise scale** (many DAGs, many users)
- **Need monitoring** and observability
- **Team collaboration** on workflows
- **Integration** with many systems
- **Audit requirements** (tracking all runs)

### ❌ **Maybe Not For:**

- **Simple daily jobs** (cron might be easier)
- **Small projects** (lightweight scheduler better)
- **Quick prototypes** (too much setup)
- **Resource-constrained** environments

---

## Comparison: Airflow vs Alternatives

| Feature | Airflow | Cron | APScheduler | Prefect |
|---------|---------|------|-------------|---------|
| **Complexity** | High | Low | Low-Medium | Medium |
| **UI** | ✅ Excellent | ❌ No | ❌ No | ✅ Good |
| **Monitoring** | ✅ Excellent | ⭐ Basic | ⭐ Basic | ✅ Good |
| **Dependencies** | ✅ Excellent | ❌ Manual | ⭐ Limited | ✅ Good |
| **Learning Curve** | ⭐⭐⭐⭐ Steep | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Medium |
| **Setup Time** | ⭐⭐⭐⭐ Long | ⭐ Quick | ⭐⭐ Medium | ⭐⭐⭐ Medium |
| **Best For** | Enterprise | Simple | Development | Modern |

---

## Getting Started with Your Airflow DAG

### 1. **Install Airflow**

```bash
pip install apache-airflow
```

### 2. **Initialize Airflow**

```bash
export AIRFLOW_HOME=/path/to/airflow_home
airflow db init
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

### 3. **Copy DAG File**

```bash
cp scheduling/airflow_dag.py $AIRFLOW_HOME/dags/price_recommendation_dag.py
```

### 4. **Start Airflow**

```bash
# Terminal 1: Web server
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler
```

### 5. **Access UI**

Open browser: `http://localhost:8080`  
Login: `admin` / `admin`

### 6. **Enable DAG**

1. Find `daily_price_recommendation` in the list
2. Toggle it **ON**
3. It will run daily at 6:00 AM automatically

---

## Summary

### What is a DAG?
- A **blueprint** of your workflow
- Shows tasks and their **dependencies**
- Defines **order** of execution

### What is Scheduling?
- **When** the DAG runs (based on cron expression)
- Airflow scheduler **checks schedules** constantly
- **Triggers** DAGs at the right time

### Your Use Case
- **DAG**: Daily price recommendation workflow
- **Schedule**: Daily at 6:00 AM
- **Tasks**: Fetch data → Generate recommendation → Notify

**Think of it as:**
- **DAG** = Recipe (what to do)
- **Schedule** = Timer (when to do it)
- **Scheduler** = Chef (executes the recipe at the right time)

---

## Further Reading

- **Airflow Documentation**: https://airflow.apache.org/docs/
- **Your DAG File**: `scheduling/airflow_dag.py`
- **Scheduling Guide**: `scheduling/SCHEDULING_README.md`

