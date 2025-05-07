import scrapy

from crawler.extractors import get_extractors
from crawler.items import DataItem


class SeedSpider(scrapy.Spider):
    name = "seed"
    def __init__(self, *args, domain=None, **kwargs):
        super().__init__(*args, **kwargs)
        # If domain is passed via -a domain=..., override start_urls
        if domain:
            self.start_urls = [domain]
    custom_settings = {
        "DEPTH_LIMIT": 1,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 3.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        # AutoThrottle to adjust delays dynamically based on server latency
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2.0,
        "AUTOTHROTTLE_MAX_DELAY": 10.0,
    }

    start_urls = [
        "https://documentation.grandstream.com",
        "https://smallbusinessphones.ca/networking-solutions/routers.html",
    ]

    def parse(self, response):
        # dynamically choose extractor based on response URL
        for extractor_cls in get_extractors():
            if extractor_cls.matches(response.url):
            for item in extractor_cls().extract(response):
                yield item
                break

        # follow links for any known extractor domains
        for href in response.css("a::attr(href)").getall():
            if href.startswith(("http://", "https://")) and any(
                extractor.matches(href) for extractor in get_extractors()
            ):
                yield response.follow(href, callback=self.parse)
