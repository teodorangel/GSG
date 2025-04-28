from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from crawler.items import DataItem


class BaseExtractor(ABC):
    """
    Interface each domain-specific extractor must implement.
    """

    @classmethod
    @abstractmethod
    def matches(cls, url: str) -> bool:
        """Return True if this extractor knows how to parse the given URL."""

    @abstractmethod
    def extract(self, response) -> List[DataItem]:  # Scrapy response
        """Return a list of DataItem objects parsed from the page."""
