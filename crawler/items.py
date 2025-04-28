from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class ItemType(str, Enum):
    PRODUCT = "product"
    MANUAL = "manual"
    VIDEO = "video"
    PAGE = "page"      # generic fallback


@dataclass
class DataItem:
    __slots__ = ('url', 'item_type', 'payload')
    """
    Container passed from extractor → pipeline.

    Attributes:
        url: Original URL of the content.
        item_type: Category of the data (see ItemType).
        payload:   Arbitrary key–value map with extracted fields.
    """
    url: str
    item_type: ItemType
    payload: Dict[str, Any]
