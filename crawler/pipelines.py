from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
from crawler.items import DataItem, ItemType
import os
from scrapy.exceptions import NotConfigured
from shared.db import SessionLocal, create_image, create_document, get_or_create_product


class CategoryImagesPipeline(ImagesPipeline):
    """
    Pipeline to download category and subcategory icons.
    """
    def __init__(self, *args, **kwargs):
        # Initialize the ImagesPipeline; disable if dependencies are missing
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            self.logger.error("CategoryImagesPipeline initialization failed: %s", e)
            raise NotConfigured("CategoryImagesPipeline disabled due to initialization error") from e

    def get_media_requests(self, item, info):
        # Only process items with an image_url in payload
        if isinstance(item, DataItem):
            image_url = item.payload.get("image_url")
            if image_url:
                yield Request(image_url, meta={"item": item})

    def file_path(self, request, response=None, info=None):
        # Save images under their original filenames
        filename = os.path.basename(request.url)
        return filename

    def item_completed(self, results, item, info):
        """
        After image downloads, persist each to the images table if product_id is provided.
        """
        # Only handle DataItem instances
        if isinstance(item, DataItem):
            session = SessionLocal()
            prod_id = item.payload.get('product_id')
            for ok, file_info in results:
                local_path = file_info.get('path')
                if ok and prod_id and local_path:
                    from os.path import basename
                    create_image(session, product_id=prod_id, url=basename(local_path))
            session.close()
        return item


class ManualFilesPipeline(FilesPipeline):
    """
    Pipeline to download manual PDF files.
    """
    def __init__(self, *args, **kwargs):
        # Initialize the FilesPipeline; disable if dependencies are missing
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            self.logger.error("ManualFilesPipeline initialization failed: %s", e)
            raise NotConfigured("ManualFilesPipeline disabled due to initialization error") from e

    def get_media_requests(self, item, info):
        # Only process items with a pdf_url in payload
        if isinstance(item, DataItem):
            pdf_url = item.payload.get("pdf_url")
            if pdf_url:
                yield Request(pdf_url, meta={"item": item})

    def file_path(self, request, response=None, info=None):
        # Save PDFs under their original filenames
        filename = os.path.basename(request.url)
        return filename

    def item_completed(self, results, item, info):
        """
        After PDF downloads, persist each to the documents table, always associating with a product using model/name from the payload.
        """
        if isinstance(item, DataItem) and 'pdf_url' in item.payload:
            session = SessionLocal()
            model = item.payload.get('model')
            name = item.payload.get('name')
            if model or name:
                # Look up or create the product
                product = get_or_create_product(session, model=model, name=name)
                for ok, file_info in results:
                    local_path = file_info.get('path')
                    if ok and local_path:
                        from os.path import basename
                        create_document(session, product_id=product.id, url=basename(local_path))
            session.close()
        return item


class ProductPipeline:
    """Pipeline to create or update products in the database and attach product_id."""
    def process_item(self, item, spider):
        if isinstance(item, DataItem) and item.item_type == ItemType.PRODUCT:
            session = SessionLocal()
            model = item.payload.get('model') or item.url
            name = item.payload.get('name') or item.payload.get('title', '')
            product = get_or_create_product(session, model=model, name=name)
            # Update other fields if present
            updated = False
            for field in ('category', 'price', 'brand'):
                if field in item.payload:
                    val = item.payload[field]
                    if getattr(product, field, None) != val:
                        setattr(product, field, val)
                        updated = True
            if updated:
                session.add(product)
                session.commit()
            # Attach product_id for downstream pipelines
            item.payload['product_id'] = product.id
            session.close()
        return item 