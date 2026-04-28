import schedule
import time
import subprocess
import logging
from datetime import datetime

# Set up logging so every run is recorded
logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s — %(message)s'
)

def run_pipeline():
    """
    Runs the full fraud detection pipeline:
    1. Reloads the dataset
    2. Recomputes features
    3. Re-scores all accounts
    4. Updates the risk registry CSV
    """
    logging.info("Pipeline started")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Running fraud detection pipeline...")
    try:
        subprocess.run(['python', 'api/refresh_registry.py'], check=True)
        logging.info("Pipeline completed successfully")
        print("Pipeline completed successfully.")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print(f"Pipeline failed: {e}")

# Schedule: run every day at 02:00 AM
schedule.every().day.at("02:00").do(run_pipeline)

# Also run immediately on startup
run_pipeline()

print("Scheduler running. Pipeline will refresh daily at 02:00 AM.")
print("Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(60)