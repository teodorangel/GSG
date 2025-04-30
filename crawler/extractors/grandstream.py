from typing import List
from bs4 import BeautifulSoup
from scrapy.http import Response
from urllib.parse import urlparse

from crawler.items import DataItem, ItemType
from crawler.extractors.base import BaseExtractor


class GrandstreamExtractor(BaseExtractor):
    """Very first cut: extract only the <title>."""

    @classmethod
    def matches(cls, url: str) -> bool:
        return "grandstream.com" in url

    def extract(self, response: Response) -> List[DataItem]:
        """
        Extract either a list of subcategories (with title, icon, and URL) if present,
        otherwise extract a simple page title.
        """
        soup = BeautifulSoup(response.text, "lxml")

        # Handle article list on product series pages (Level 4)
        article_links = soup.select("ul.hkb-category__articlelist li a")
        if article_links:
            items: List[DataItem] = []
            for a in article_links:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                items.append(
                    DataItem(
                        url=href,
                        item_type=ItemType.PAGE,
                        payload={"title": title, "branch": "article", "url": href},
                    )
                )
            return items

        # Handle PDF manual download links on manual pages (Level 5)
        pdf_links = soup.select("a[download] img")
        if pdf_links:
            items: List[DataItem] = []
            for img in pdf_links:
                link = img.parent
                pdf_url = link.get("href", "")
                icon_url = img.get("src", "")
                # Derive a simple title from the filename
                filename = pdf_url.split("/")[-1]
                title = filename.replace(".pdf", "").replace("-", " ")
                items.append(
                    DataItem(
                        url=pdf_url,
                        item_type=ItemType.PAGE,
                        payload={
                            "title": title,
                            "branch": "manual",
                            "pdf_url": pdf_url,
                            "icon_url": icon_url,
                        },
                    )
                )
            return items

        # Look for subcategory blocks on category pages
        sub_links = soup.select("a.hkb-category__link")
        if sub_links:
            def classify_branch(href: str) -> str:
                path = urlparse(href).path.rstrip('/')
                if path.endswith('-series'):
                    return 'series'
                # any deeper article-categories is a subcategory
                if '/article-categories/' in path:
                    return 'subcategory'
                return 'category'
            
            items: List[DataItem] = []
            for link in sub_links:
                href = link.get("href", "")
                # Title is inside <h2 class="hkb-category__title">
                title_tag = link.select_one(".hkb-category__title")
                title = title_tag.get_text(strip=True) if title_tag else ""
                # Icon image
                img_tag = link.select_one(".hkb-category__iconwrap img")
                image_url = img_tag.get("src", "") if img_tag else ""
                items.append(
                    DataItem(
                        url=href,
                        item_type=ItemType.PAGE,
                        payload={
                            "title": title,
                            "image_url": image_url,
                            "branch": classify_branch(href)
                        },
                    )
                )
            return items

        # Fallback to simple page title extraction
        title = (soup.title.string or "").strip() if soup.title else "Untitled"
        return [
            DataItem(
                url=response.url,
                item_type=ItemType.PAGE,
                payload={"title": title},
            )
        ]
