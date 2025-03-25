"""
Scrapy settings for the realestate project

This file contains all the Scrapy settings for the project.
"""

import os
import random

BOT_NAME = "realestate"

SPIDER_MODULES = ["realestate.spiders"]
NEWSPIDER_MODULE = "realestate.spiders"

# Crawl responsibly by identifying yourself on the user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Obey robots.txt rules (set to False to bypass restrictions - use responsibly)
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8

# Configure delay for requests for the same website
DOWNLOAD_DELAY = random.uniform(1.0, 3.0)  # Random delay between 1-3 seconds
RANDOMIZE_DOWNLOAD_DELAY = True

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    "realestate.middlewares.RealEstateSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "realestate.middlewares.RealEstateDownloaderMiddleware": 543,
    "realestate.middlewares.UserAgentRotatorMiddleware": 400,
    "realestate.middlewares.ProxyMiddleware": 350,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 400,
}

# Configure item pipelines
ITEM_PIPELINES = {
    "realestate.pipelines.MongoPipeline": 300,
    "realestate.pipelines.DuplicateDetectionPipeline": 100,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# MongoDB settings
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = "realestate"
MONGODB_COLLECTION = "properties"

# Configure maximum number of retries for a request
RETRY_TIMES = 10
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# Configure proxy settings
USE_PROXY = True
PROXY_LIST = os.environ.get("PROXY_LIST", "").split(",") if os.environ.get("PROXY_LIST") else []

# Configure logging
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"
