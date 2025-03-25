"""
Define scrapy middlewares for handling proxy rotation, user agent rotation, and other anti-detection measures
"""

import random
import logging
import time
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.exceptions import IgnoreRequest

from .utils.user_agent_rotator import UserAgentRotator
from .utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)


class RealEstateSpiderMiddleware:
    """Spider middleware for the real estate scraper"""
    
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class RealEstateDownloaderMiddleware:
    """Downloader middleware for the real estate scraper"""
    
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Add random delays to simulate human behavior
        time.sleep(random.uniform(0.5, 2.0))
        return None

    def process_response(self, request, response, spider):
        # Check if we've been blocked or given a CAPTCHA
        if self._is_blocked(response):
            logger.warning(f"Detected blocking behavior from {request.url}")
            raise IgnoreRequest("Request was blocked")
            
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
        
    def _is_blocked(self, response):
        """Check if the response indicates we've been blocked"""
        if response.status in [403, 429]:
            return True
            
        # Check for CAPTCHA or other block indicators in content
        captcha_indicators = [
            'captcha', 'blocked', 'security check', 'robot', 
            'automated', 'suspicious activity'
        ]
        
        content_lower = response.text.lower()
        for indicator in captcha_indicators:
            if indicator in content_lower:
                return True
                
        return False


class UserAgentRotatorMiddleware:
    """Middleware to rotate user agents for each request"""
    
    def __init__(self):
        self.user_agent_rotator = UserAgentRotator()
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
        
    def process_request(self, request, spider):
        user_agent = self.user_agent_rotator.get_random_user_agent()
        request.headers['User-Agent'] = user_agent
        logger.debug(f"Using User-Agent: {user_agent}")
        return None
        
    def spider_opened(self, spider):
        spider.logger.info("UserAgentRotatorMiddleware enabled")


class ProxyMiddleware:
    """Middleware to rotate proxies for each request"""
    
    def __init__(self, settings):
        self.use_proxy = settings.getbool('USE_PROXY', False)
        self.proxy_manager = ProxyManager(settings)
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.settings)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
        
    def process_request(self, request, spider):
        if not self.use_proxy:
            return None
            
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            request.meta['proxy'] = proxy
            logger.debug(f"Using proxy: {proxy}")
        return None
        
    def process_response(self, request, response, spider):
        # If we get blocked, mark the proxy as failed if we're using one
        if response.status in [403, 429] and 'proxy' in request.meta:
            proxy = request.meta['proxy']
            self.proxy_manager.mark_proxy_failed(proxy)
            logger.warning(f"Proxy {proxy} failed with status {response.status}")
        return response
        
    def process_exception(self, request, exception, spider):
        # If we get an exception, mark the proxy as failed if we're using one
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            self.proxy_manager.mark_proxy_failed(proxy)
            logger.warning(f"Proxy {proxy} failed with exception: {str(exception)}")
        
    def spider_opened(self, spider):
        if self.use_proxy:
            spider.logger.info("ProxyMiddleware enabled")
        else:
            spider.logger.info("ProxyMiddleware disabled")
