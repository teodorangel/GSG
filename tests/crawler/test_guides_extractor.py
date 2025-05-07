import pytest
from scrapy.http import TextResponse

from crawler.extractors.guides import GuidesExtractor
from crawler.items import ItemType


def test_guides_extractor_happy_path():
    html = '''
    <html>
      <head><title>Guide Index</title></head>
      <body>
        <div class="toctree-wrapper">
          <ul>
            <li><a href="guide1.html">Guide One</a></li>
            <li><a href="guide2.html">Guide Two</a></li>
          </ul>
        </div>
      </body>
    </html>
    '''
    url = "https://documentation.grandstream.com/index.html"
    response = TextResponse(url=url, body=html.encode('utf-8'), encoding='utf-8')

    extractor = GuidesExtractor()
    items = extractor.extract(response)

    assert len(items) == 2
    # First guide
    first = items[0]
    assert first.item_type == ItemType.PAGE
    assert first.url == "https://documentation.grandstream.com/guide1.html"
    assert first.payload["title"] == "Guide One"
    assert first.payload["url"] == first.url

    # Second guide
    second = items[1]
    assert second.item_type == ItemType.PAGE
    assert second.url == "https://documentation.grandstream.com/guide2.html"
    assert second.payload["title"] == "Guide Two"
    assert second.payload["url"] == second.url


def test_guides_extractor_fallback():
    html = '''
    <html>
      <head><title>Only Title</title></head>
      <body><p>No guides here</p></body>
    </html>
    '''
    url = "https://documentation.grandstream.com/page.html"
    response = TextResponse(url=url, body=html.encode('utf-8'), encoding='utf-8')

    extractor = GuidesExtractor()
    items = extractor.extract(response)

    assert len(items) == 1
    only = items[0]
    assert only.item_type == ItemType.PAGE
    assert only.url == url
    assert only.payload["title"] == "Only Title"
    # Fallback payload does not include 'url' key aside from the item.url
    assert "url" not in only.payload or only.payload.get("url") == url 