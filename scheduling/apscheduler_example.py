# scheduling/apscheduler_example.py
"""
APScheduler example for simple scheduling without external services.

Install APScheduler:
    pip install apscheduler

Run scheduler:
    python scheduling/apscheduler_example.py

This will run the batch job on schedule in the background.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.batch_job import run_daily_recommendation

def daily_recommendation_job():
    """Job function to run daily recommendation."""
    print(f"\n{'='*60}")
    print(f"Running scheduled job at {datetime.now()}")
    print(f"{'='*60}\n")
    
    try:
        recommendation = run_daily_recommendation()
        print(f"\n✓ Job completed successfully")
        print(f"  Recommended Price: ₹{recommendation['recommended_price']:.2f}")
        return recommendation
    except Exception as e:
        print(f"\n✗ Job failed: {e}")
        raise

def main():
    """Main function to start the scheduler."""
    print("Starting APScheduler for daily price recommendations...")
    print("Schedule: Daily at 6:00 AM")
    print("Press Ctrl+C to stop\n")
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Add job - runs daily at 6:00 AM
    scheduler.add_job(
        func=daily_recommendation_job,
        trigger=CronTrigger(hour=6, minute=0),
        id='daily_price_recommendation',
        name='Daily Price Recommendation',
        replace_existing=True,
    )
    
    print("Scheduler started. Jobs will run on schedule.")
    print("Current time:", datetime.now())
    print("Next run:", scheduler.get_job('daily_price_recommendation').next_run_time)
    print("\nWaiting for scheduled time...\n")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        scheduler.shutdown()

if __name__ == "__main__":
    main()

