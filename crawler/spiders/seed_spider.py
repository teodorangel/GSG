import scrapy

from crawler.extractors import grandstream
from crawler.items import DataItem


class SeedSpider(scrapy.Spider):
    name = "seed"
    custom_settings = {
        "DEPTH_LIMIT": 1,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
    }

    start_urls = ["https://grandstream.com/products"]

    def parse(self, response):
        # choose extractor
        extractor_cls = (
            grandstream.GrandstreamExtractor
            if grandstream.GrandstreamExtractor.matches(response.url)
            else None
        )
        if extractor_cls:
            for item in extractor_cls().extract(response):
                yield item

        # follow links within same domain up to depth limit
        for href in response.css("a::attr(href)").getall():
            if href.startswith(("http://", "https://")) and "grandstream.com" in href:
                yield response.follow(href, callback=self.parse)
