from typing import List
from scrapy.http import Response
from crawler.extractors.base import BaseExtractor
from crawler.items import DataItem, ItemType

class SmallbusinessExtractor(BaseExtractor):
    """
    Extractor for the Small Business Phones Canada routers page.
    """
    @classmethod
    def matches(cls, url: str) -> bool:
        # Match any smallbusinessphones.ca page
        return "smallbusinessphones.ca" in url

    def extract(self, response: Response) -> List[DataItem]:
        items: List[DataItem] = []
        # Select products by new img classes or legacy container
        for img in response.css('img.ty-pict.lazyOwl.cm-image.abt-ut2-lazy-loaded, img.ty-pict.lazyOwl.cm-image, #category_products_11 img'):
            # Find the nearest ancestor link
            parent_link = img.xpath('ancestor::a[@href][1]')
            link = parent_link.xpath('@href').get()
            # Prefer the lazy-loaded URL
            src = img.attrib.get('data-src') or img.attrib.get('src')
            if not link or not src:
                continue
            full_link = response.urljoin(link)
            full_img = response.urljoin(src)
            # Use alt or title attribute for description
            title = img.attrib.get('alt') or img.attrib.get('title') or full_link
            payload = {
                'title': title.strip(),
                'image_url': full_img,
            }
            items.append(DataItem(
                url=full_link,
                item_type=ItemType.PRODUCT,
                payload=payload,
            ))
        # Fallback: if no products found, yield page title as a single item
        if not items:
            title = response.css('title::text').get(default='').strip()
            items.append(
                DataItem(
                    url=response.url,
                    item_type=ItemType.PAGE,
                    payload={'title': title},
                )
            )
        return items 