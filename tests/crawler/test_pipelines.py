import pytest
from crawler.items import DataItem, ItemType
from crawler.pipelines import CategoryImagesPipeline, ManualFilesPipeline, ProductPipeline
from scrapy import Request


def test_category_images_pipeline_request():
    item = DataItem(url='http://example.com', item_type=ItemType.PAGE, payload={'image_url': 'http://example.com/img.png'})
    pipeline = CategoryImagesPipeline()
    reqs = list(pipeline.get_media_requests(item, None))
    assert len(reqs) == 1
    assert isinstance(reqs[0], Request)
    assert reqs[0].url == 'http://example.com/img.png'


def test_category_images_pipeline_no_request():
    item = DataItem(url='http://example.com', item_type=ItemType.PAGE, payload={})
    pipeline = CategoryImagesPipeline()
    assert list(pipeline.get_media_requests(item, None)) == []


def test_category_images_file_path():
    pipeline = CategoryImagesPipeline()
    fake_req = Request('http://example.com/images/pic.jpg')
    assert pipeline.file_path(fake_req) == 'pic.jpg'


def test_manual_files_pipeline_request():
    item = DataItem(url='http://example.com', item_type=ItemType.PAGE, payload={'pdf_url': 'http://example.com/file.pdf'})
    pipeline = ManualFilesPipeline()
    reqs = list(pipeline.get_media_requests(item, None))
    assert len(reqs) == 1
    assert isinstance(reqs[0], Request)
    assert reqs[0].url == 'http://example.com/file.pdf'


def test_manual_files_pipeline_no_request():
    item = DataItem(url='http://example.com', item_type=ItemType.PAGE, payload={})
    pipeline = ManualFilesPipeline()
    assert list(pipeline.get_media_requests(item, None)) == []


def test_manual_files_file_path():
    pipeline = ManualFilesPipeline()
    fake_req = Request('http://example.com/docs/doc.pdf')
    assert pipeline.file_path(fake_req) == 'doc.pdf' 


# Tests for ProductPipeline: ensure it upserts and attaches product_id
def test_product_pipeline_upsert_and_attach_id(monkeypatch):
    from crawler.pipelines import SessionLocal, get_or_create_product, ProductPipeline
    from crawler.items import DataItem, ItemType

    # Dummy product and session to inject
    class DummyProduct:
        def __init__(self):
            self.id = 999
            self.category = None
            self.price = None
            self.brand = None

    class DummySession:
        def __init__(self):
            self.closed = False
            self.committed = False
        def add(self, obj): pass
        def commit(self): self.committed = True
        def close(self): self.closed = True

    dummy_product = DummyProduct()
    monkeypatch.setattr('crawler.pipelines.SessionLocal', lambda: DummySession())
    monkeypatch.setattr('crawler.pipelines.get_or_create_product', lambda session, model, name: dummy_product)

    # Prepare DataItem with product payload
    payload = {'title': 'TestProd', 'category': 'CatTest', 'price': 12.34, 'brand': 'BrandTest'}
    item = DataItem(url='http://example.com/test', item_type=ItemType.PRODUCT, payload=payload.copy())

    pipeline = ProductPipeline()
    processed = pipeline.process_item(item, spider=None)

    # Ensure product_id is attached and payload preserved
    assert processed.payload['product_id'] == dummy_product.id
    for key, val in payload.items():
        assert processed.payload[key] == val 