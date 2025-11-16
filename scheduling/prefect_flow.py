# scheduling/prefect_flow.py
"""
Prefect workflow for daily price recommendation scheduling.

Install Prefect:
    pip install prefect prefect-sqlalchemy

Run Prefect server:
    prefect server start

Create and run flow:
    python scheduling/prefect_flow.py

Schedule in Prefect Cloud:
    prefect cloud login
    prefect deployment build scheduling/prefect_flow.py:price_recommendation_flow -n daily-recommendations --cron "0 6 * * *"
    prefect deployment apply price_recommendation_flow-deployment.yaml
    prefect deployment run price_recommendation_flow/daily-recommendations
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from prefect import flow, task, get_run_logger
from prefect.task_runners import SequentialTaskRunner
from prefect.schedules import CronSchedule
from src.batch_job import run_daily_recommendation

@task(name="fetch_today_data")
def fetch_today_data_task(date: str = None):
    """Task to fetch today's market data."""
    logger = get_run_logger()
    logger.info(f"Fetching today's data for date: {date}")
    
    # In production, this would call an API or database
    # For now, uses the batch_job function's logic
    return date or datetime.now().strftime('%Y-%m-%d')

@task(name="generate_recommendation")
def generate_recommendation_task(date: str):
    """Task to generate price recommendation."""
    logger = get_run_logger()
    logger.info(f"Generating recommendation for {date}")
    
    try:
        recommendation = run_daily_recommendation(date=date)
        logger.info(f"Recommendation generated successfully: {recommendation['recommended_price']}")
        return recommendation
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise

@task(name="notify_stakeholders")
def notify_stakeholders_task(recommendation: dict):
    """Task to notify stakeholders (placeholder for integration)."""
    logger = get_run_logger()
    logger.info(f"Notifying stakeholders of recommendation: {recommendation['recommended_price']}")
    
    # In production, this could:
    # - Send email notifications
    # - Post to Slack/Teams
    # - Update dashboard
    # - Trigger downstream systems
    
    logger.info("Notification sent successfully")
    return True

@flow(
    name="price_recommendation_flow",
    description="Daily fuel price recommendation workflow",
    task_runner=SequentialTaskRunner(),
    # Schedule to run daily at 6:00 AM
    schedule=CronSchedule(cron="0 6 * * *", timezone="UTC"),
)
def price_recommendation_flow(date: str = None):
    """
    Main Prefect flow for daily price recommendations.
    
    Args:
        date: Date string (YYYY-MM-DD). If None, uses today.
    """
    logger = get_run_logger()
    logger.info("Starting price recommendation flow")
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Step 1: Fetch today's data
    today_date = fetch_today_data_task(date)
    
    # Step 2: Generate recommendation
    recommendation = generate_recommendation_task(today_date)
    
    # Step 3: Notify stakeholders (optional)
    notify_stakeholders_task(recommendation)
    
    logger.info("Price recommendation flow completed successfully")
    return recommendation

# For running without scheduler (manual execution)
if __name__ == "__main__":
    # Run the flow manually
    result = price_recommendation_flow()
    print(f"Flow completed: {result}")

