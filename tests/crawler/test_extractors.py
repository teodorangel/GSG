from pathlib import Path
from crawler.extractors.grandstream import GrandstreamExtractor

SAMPLE_HTML = """
<html><head><title>GXV3370 High-End IP Video Phone</title></head>
<body><h1>GXV3370</h1></body></html>
""".strip()


def test_matches():
    assert GrandstreamExtractor.matches("https://grandstream.com/products/gxv3370")


def test_title_extraction():
    resp = type("FakeResponse", (), {"text": SAMPLE_HTML, "url": "https://grandstream.com/x"})()
    items = GrandstreamExtractor().extract(resp)
    assert items[0].payload["title"] == "GXV3370 High-End IP Video Phone"
