import scrapy

from crawler.extractors import get_extractors
from crawler.items import DataItem, ItemType


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
        # Extract product context from meta or page (customize as needed)
        product_model = response.meta.get('product_model')
        product_name = response.meta.get('product_name')

        # If the response is a PDF, yield as document with context
        content_type = response.headers.get('Content-Type', b'').decode().lower()
        if 'application/pdf' in content_type or response.url.lower().endswith('.pdf'):
            if product_model or product_name:
                yield DataItem(
                    url=response.url,
                    item_type=ItemType.DOCUMENT,
                    payload={
                        'pdf_url': response.url,
                        'model': product_model,
                        'name': product_name,
                    }
                )
            return  # Don't parse further if it's a PDF

        # Use extractors as before
        for extractor_cls in get_extractors():
            if extractor_cls.matches(response.url):
                for item in extractor_cls().extract(response):
                    # If the item is a product, update context
                    if hasattr(item, 'item_type') and item.item_type == ItemType.PRODUCT:
                        product_model = item.payload.get('model')
                        product_name = item.payload.get('name')
                    yield item
                break

        # For every <a> link
        for href in response.css("a::attr(href)").getall():
            if href.lower().endswith('.pdf'):
                # Direct PDF link: yield as document with context
                if product_model or product_name:
                    yield DataItem(
                        url=href,
                        item_type=ItemType.DOCUMENT,
                        payload={
                            'pdf_url': href,
                            'model': product_model,
                            'name': product_name,
                        }
                    )
            elif href.startswith(("http://", "https://")) and any(
                extractor.matches(href) for extractor in get_extractors()
            ):
                # Not a PDF: follow the link for further parsing, pass context
                yield response.follow(
                    href,
                    callback=self.parse,
                    meta={
                        'product_model': product_model,
                        'product_name': product_name,
                    }
                )
