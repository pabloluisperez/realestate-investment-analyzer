"""
Scheduler for running the web scraper at regular intervals.
Uses APScheduler to manage periodic tasks.
"""

import logging
import os
import sys
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from realestate.spiders.idealista import IdealistaSpider
from realestate.spiders.fotocasa import FotocasaSpider

logger = logging.getLogger(__name__)


def run_spider(spider_class):
    """Run a Scrapy spider using CrawlerProcess"""
    try:
        logger.info(f"Starting spider: {spider_class.name}")
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        process.crawl(spider_class)
        process.start()  # This will block until the crawling is finished
        logger.info(f"Finished spider: {spider_class.name}")
    except Exception as e:
        logger.error(f"Error running spider {spider_class.name}: {str(e)}")


def run_all_spiders():
    """Run all configured spiders"""
    try:
        logger.info("Starting all spiders")
        start_time = datetime.now()
        
        # Run Idealista spider
        run_spider(IdealistaSpider)
        
        # Run Fotocasa spider
        run_spider(FotocasaSpider)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60.0
        logger.info(f"All spiders completed in {duration:.2f} minutes")
    except Exception as e:
        logger.error(f"Error running spiders: {str(e)}")


def start_scheduler():
    """Configure and start the background scheduler"""
    try:
        logger.info("Initializing scheduler")
        scheduler = BackgroundScheduler()
        
        # Run spiders daily at 1:00 AM
        scheduler.add_job(
            run_all_spiders,
            trigger=CronTrigger(hour=1, minute=0),
            id='daily_scraping',
            name='Run all real estate spiders every day at 1:00 AM',
            replace_existing=True
        )
        
        # Run immediately on startup
        scheduler.add_job(
            run_all_spiders,
            id='initial_scraping',
            name='Initial scraping on startup',
            next_run_time=datetime.now()
        )
        
        scheduler.start()
        logger.info("Scheduler started successfully")
        
        # Keep the main thread running to allow scheduler to work
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler")
            scheduler.shutdown()
            sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # If run directly, start the scheduler
    start_scheduler()
