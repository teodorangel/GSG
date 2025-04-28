from typing import List
from bs4 import BeautifulSoup
from scrapy.http import Response

from crawler.items import DataItem, ItemType
from crawler.extractors.base import BaseExtractor


class GrandstreamExtractor(BaseExtractor):
    """Very first cut: extract only the <title>."""

    @classmethod
    def matches(cls, url: str) -> bool:
        return "grandstream.com" in url

    def extract(self, response: Response) -> List[DataItem]:
        soup = BeautifulSoup(response.text, "lxml")

        title = (soup.title.string or "").strip() if soup.title else "Untitled"
        return [
            DataItem(
                url=response.url,
                item_type=ItemType.PAGE,
                payload={"title": title},
            )
        ]
