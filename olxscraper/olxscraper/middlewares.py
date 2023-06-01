# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import requests
import base64
from random import randint
from urllib.parse import urlencode

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class OlxscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class OlxscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class FakeBrowserHeaderAgentMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):

        scrapeops_config = settings.get('SCRAPEOPS_CONFIG')

        self.api_key = scrapeops_config.get('api_key', '')
        self.num_results = scrapeops_config.get('num_results')
        self.is_active = scrapeops_config['browser_headers'].get('enabled', True)
        self.endpoint = scrapeops_config['browser_headers'].get(
            'endpoint', 'https://headers.scrapeops.io/v1/browser-headers'
        )
        self.headers_list = []

        self._get_headers_list()
        self._is_active()

    def _get_headers_list(self):
        payload = {'api_key': self.api_key}
        if self.num_results is not None:
            payload['num_headers'] = self.num_results

        response = requests.get(self.endpoint, params=urlencode(payload))
        json_response = response.json()
        self.headers_list = json_response.get('result', [])

    def _get_random_browser_header(self):
        random_index = randint(0, len(self.headers_list) - 1)
        return self.headers_list[random_index]

    def _is_active(self):
        if self.api_key is None or self.api_key == '' or not self.is_active:
            self.is_active = False
        else:
            self.is_active = True

    def process_request(self, request, spider):
        if self.is_active:
            random_browser_header = self._get_random_browser_header()
            request.headers['accept-language'] = random_browser_header['accept-language']
            request.headers['sec-fetch-user'] = random_browser_header['sec-fetch-user']
            request.headers['sec-fetch-mod'] = random_browser_header['sec-fetch-mod']
            request.headers['sec-fetch-site'] = random_browser_header['sec-fetch-site']
            request.headers['sec-ch-ua-platform'] = random_browser_header['sec-ch-ua-platform']
            request.headers['sec-ch-ua-mobile'] = random_browser_header['sec-ch-ua-mobile']
            request.headers['sec-ch-ua'] = random_browser_header['sec-ch-ua']
            request.headers['accept'] = random_browser_header['accept']
            request.headers['user-agent'] = random_browser_header['user-agent']
            request.headers['upgrade-insecure-requests'] = random_browser_header.get('upgrade-insecure-requests', '')


class ProxyMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        config = settings.get('PROXY_CONFIG')
        self.username = config.get('username')
        self.password = config.get('password')
        self.endpoint = config.get('endpoint')
        self.port = config.get('port')

        self.is_active = config.get('enabled', True)
        self._is_active()

    def _all_params_set(self):
        if self.username is None or self.username == '' or \
           self.password is None or self.password == '' or \
           self.endpoint is None or self.endpoint == '' or \
           self.port is None or self.port == '':
            return False
        return True

    def _is_active(self):
        if not self._all_params_set() or not self.is_active:
            self.is_active = False
        else:
            self.is_active = True

    def process_request(self, request, spider):
        if self.is_active:
            host = f'http://{self.endpoint}:{self.port}'
            auth_string = f'{self.username}:{self.password}'
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            request.meta['proxy'] = host
            request.headers['Proxy-Authorization'] = f'Basic {encoded_auth}'
