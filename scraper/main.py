"""
Main entry point for the real estate scraper application.
This script initializes the scheduler that runs periodic scraping tasks.
"""

import os
import sys
import logging
from scheduler import start_scheduler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting Real Estate Scraper")
        # Start the scheduler for periodic scraping
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scraper: {str(e)}")
        sys.exit(1)
