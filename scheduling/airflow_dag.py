# scheduling/airflow_dag.py
"""
Apache Airflow DAG for daily price recommendation scheduling.

Install Airflow:
    pip install apache-airflow

Initialize Airflow:
    airflow db init
    airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

Start Airflow:
    airflow webserver --port 8080
    airflow scheduler

Place this file in: AIRFLOW_HOME/dags/price_recommendation_dag.py

Access Airflow UI:
    http://localhost:8080 (admin/admin)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import sys
from pathlib import Path

# Add project to path (assumes DAG is in scheduling/ folder of the project)
try:
    # Try to find the project root relative to this file
    PROJECT_PATH = Path(__file__).resolve().parent.parent
    if str(PROJECT_PATH) not in sys.path:
        sys.path.insert(0, str(PROJECT_PATH))
except Exception:
    # Fallback if __file__ is not available (some Airflow setups)
    # You may need to set PYTHONPATH env var in Airflow
    pass

from src.batch_job import run_daily_recommendation

# Default arguments for the DAG
default_args = {
    'owner': 'ml-engineer',
    'depends_on_past': False,
    'email': ['admin@example.com'],  # Configure email in airflow.cfg
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'daily_price_recommendation',
    default_args=default_args,
    description='Daily fuel price recommendation job',
    schedule_interval='30 20 * * *',  # Run daily at 8:30 PM
    catchup=False,  # Don't backfill missed runs
    tags=['price', 'optimization', 'ml'],
)

def fetch_today_data(**context):
    """Fetch today's market data."""
    execution_date = context['execution_date']
    date = execution_date.strftime('%Y-%m-%d')
    print(f"Fetching data for date: {date}")
    return date

def generate_recommendation(**context):
    """Generate price recommendation."""
    ti = context['ti']
    date = ti.xcom_pull(task_ids='fetch_today_data')
    
    print(f"Generating recommendation for {date}")
    try:
        recommendation = run_daily_recommendation(date=date)
        print(f"Recommendation: {recommendation['recommended_price']}")
        return recommendation
    except Exception as e:
        print(f"Error: {e}")
        raise

def notify_stakeholders(**context):
    """Notify stakeholders (placeholder)."""
    ti = context['ti']
    recommendation = ti.xcom_pull(task_ids='generate_recommendation')
    
    print(f"Notifying stakeholders of recommendation: {recommendation['recommended_price']}")
    # In production: Send email, Slack notification, etc.
    return True

# Define tasks
task_fetch_data = PythonOperator(
    task_id='fetch_today_data',
    python_callable=fetch_today_data,
    dag=dag,
)

task_generate_recommendation = PythonOperator(
    task_id='generate_recommendation',
    python_callable=generate_recommendation,
    dag=dag,
)

task_notify = PythonOperator(
    task_id='notify_stakeholders',
    python_callable=notify_stakeholders,
    dag=dag,
)

# Alternative: Using BashOperator if Python path is complex
task_bash_recommendation = BashOperator(
    task_id='run_recommendation_bash',
    bash_command=f'cd {PROJECT_PATH} && source venv/bin/activate && python src/batch_job.py --date {{{{ ds }}}}',
    dag=dag,
)

# Define task dependencies
task_fetch_data >> task_generate_recommendation >> task_notify

# Uncomment to use bash operator instead:
# task_bash_recommendation >> task_notify

