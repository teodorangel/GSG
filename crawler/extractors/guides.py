from typing import List
from scrapy.http import Response
from crawler.extractors.base import BaseExtractor
from crawler.items import DataItem, ItemType

class GuidesExtractor(BaseExtractor):
    """
    Extractor for Grandstream documentation guides pages.
    """
    @classmethod
    def matches(cls, url: str) -> bool:
        return "documentation.grandstream.com" in url

    def extract(self, response: Response) -> List[DataItem]:
        items: List[DataItem] = []
        # Extract links from the Sphinx toctree wrapper
        for href in response.css('div.toctree-wrapper a::attr(href)').getall():
            full_url = response.urljoin(href)
            title = response.css(f'div.toctree-wrapper a[href="{href}"]::text').get()
            text = title.strip() if title else full_url
            items.append(DataItem(
                url=full_url,
                item_type=ItemType.PAGE,
                payload={"title": text, "url": full_url},
            ))
        # Fallback to simple title if no guide links found
        if not items:
            page_title = response.css('title::text').get(default='').strip()
            items.append(DataItem(
                url=response.url,
                item_type=ItemType.PAGE,
                payload={"title": page_title},
            ))
        return items 