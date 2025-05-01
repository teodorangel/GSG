from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
from crawler.items import DataItem
import os


class CategoryImagesPipeline(ImagesPipeline):
    """
    Pipeline to download category and subcategory icons.
    """
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


class ManualFilesPipeline(FilesPipeline):
    """
    Pipeline to download manual PDF files.
    """
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