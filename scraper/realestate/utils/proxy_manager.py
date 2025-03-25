"""
Proxy management utility to rotate IP addresses and avoid detection
"""

import logging
import random
import requests
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProxyManager:
    """
    Manages a pool of proxies for rotating IP addresses during scraping.
    Keeps track of proxy health and rotates to avoid detection.
    """
    
    def __init__(self, settings):
        """Initialize the proxy manager with settings"""
        self.settings = settings
        self.proxies = self._load_proxies()
        self.failed_proxies = {}  # Track failed proxies with timestamps
        self.current_proxy = None
        self.proxy_change_interval = 10  # Change proxy every 10 requests
        self.request_count = 0
        
    def _load_proxies(self):
        """Load proxies from settings or environment variables"""
        proxies = self.settings.get('PROXY_LIST', [])
        
        if not proxies:
            logger.warning("No proxies configured. Scraping without proxy rotation may lead to IP blocking.")
            return []
            
        logger.info(f"Loaded {len(proxies)} proxies")
        return proxies
    
    def get_proxy(self):
        """Get a proxy from the pool, rotating based on usage and health"""
        if not self.proxies:
            return None
            
        # Check if we need to rotate to a new proxy
        if self.current_proxy is None or self.request_count >= self.proxy_change_interval:
            self.current_proxy = self._select_next_proxy()
            self.request_count = 0
        
        self.request_count += 1
        return self.current_proxy
    
    def _select_next_proxy(self):
        """Select the next proxy, avoiding recently failed ones"""
        # Filter out recently failed proxies
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies or 
                             datetime.now() - self.failed_proxies[p] > timedelta(minutes=30)]
        
        if not available_proxies:
            # If all proxies have failed recently, use the least recently failed one
            if self.failed_proxies:
                proxy = min(self.failed_proxies.items(), key=lambda x: x[1])[0]
                logger.warning(f"All proxies have failed recently. Using least recently failed: {proxy}")
                return proxy
            return None
        
        # Select a random proxy from available ones
        proxy = random.choice(available_proxies)
        logger.debug(f"Selected proxy: {proxy}")
        return proxy
    
    def mark_proxy_failed(self, proxy):
        """Mark a proxy as failed with the current timestamp"""
        if proxy:
            self.failed_proxies[proxy] = datetime.now()
            logger.warning(f"Marked proxy as failed: {proxy}")
            
            # If this was the current proxy, select a new one
            if proxy == self.current_proxy:
                self.current_proxy = None
    
    def test_proxies(self):
        """Test all proxies and remove non-working ones"""
        working_proxies = []
        
        for proxy in self.proxies:
            if self._test_proxy(proxy):
                working_proxies.append(proxy)
                
        self.proxies = working_proxies
        logger.info(f"{len(working_proxies)} working proxies available")
        
    def _test_proxy(self, proxy):
        """Test if a proxy is working by making a request to a test URL"""
        try:
            test_url = "https://httpbin.org/ip"
            proxies = {
                "http": proxy,
                "https": proxy
            }
            
            response = requests.get(test_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                logger.debug(f"Proxy {proxy} is working")
                return True
                
            logger.warning(f"Proxy {proxy} returned status code {response.status_code}")
            return False
        except Exception as e:
            logger.warning(f"Proxy {proxy} test failed: {str(e)}")
            return False
