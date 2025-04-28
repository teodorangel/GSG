from crawler.items import DataItem, ItemType


def test_dataitem():
    item = DataItem(url="https://x", item_type=ItemType.PAGE, payload={"title": "A"})
    assert item.item_type == ItemType.PAGE
    assert "title" in item.payload
