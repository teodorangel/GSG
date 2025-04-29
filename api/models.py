from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ProductOut(BaseModel):  # type: ignore
    """
    Output schema for a single product.

    Attributes:
        id (int): Unique product identifier.
        model (str): Model number or code.
        name (Optional[str]): Product name.
        category (Optional[str]): Product category.
        price (Optional[float]): Product price.
        brand (Optional[str]): Brand name.
        created_at (datetime): Record creation timestamp.
    """
    id: int
    model: str
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    created_at: datetime


class ProductListOut(BaseModel):  # type: ignore
    """
    Output schema for a list of products.

    Attributes:
        items (List[ProductOut]): List of products.
        total (int): Total number of products.
    """
    items: List[ProductOut]
    total: int


# Crawl endpoint schemas
class CrawlRequest(BaseModel):  # type: ignore
    """
    Request schema for initiating a crawl.

    Attributes:
        domain (str): Domain to crawl.
        depth (Optional[int]): Crawl depth (default=1).
        concurrency (Optional[int]): Concurrent fetch count (default=2).
        delay (Optional[float]): Delay between requests in seconds (default=1.0).
    """
    domain: str
    depth: Optional[int] = 1
    concurrency: Optional[int] = 2
    delay: Optional[float] = 1.0


class CrawlResponse(BaseModel):  # type: ignore
    """
    Response schema for crawl initiation.

    Attributes:
        job_id (str): Unique job identifier.
        status (str): Status of the crawl job (e.g. "created", "queued").
    """
    job_id: str
    status: str


# QA endpoint schemas
class QARequest(BaseModel):  # type: ignore
    """
    Request schema for QA endpoint.

    Attributes:
        query (str): The question to ask.
        product_id (Optional[int]): Optional product ID context.
    """
    query: str
    product_id: Optional[int] = None


class QAResponse(BaseModel):  # type: ignore
    """
    Response schema for QA endpoint.

    Attributes:
        answer (str): The answer from the QA agent.
        sources (List[str]): List of source document references.
    """
    answer: str
    sources: List[str]


# Logs streaming schema
class LogMessage(BaseModel):  # type: ignore
    """
    Schema for a single log message in the WebSocket stream.

    Attributes:
        job_id (str): The associated job ID.
        url (str): The URL being processed.
        status (str): Status of the log event (e.g. "started", "fetched", "error").
        detail (Optional[str]): Additional details or error message.
        timestamp (datetime): Timestamp of the log event.
    """
    job_id: str
    url: str
    status: str
    detail: Optional[str] = None
    timestamp: datetime


# Planning endpoint schemas
class PlanRequest(BaseModel):  # type: ignore
    """
    Request schema for project planning.

    Attributes:
        product_ids (List[int]): List of product IDs.
        budget (Optional[float]): Budget constraint.
        site_size_sqft (Optional[int]): Site size in square feet.
    """
    product_ids: List[int]
    budget: Optional[float] = None
    site_size_sqft: Optional[int] = None


class PlanResponse(BaseModel):  # type: ignore
    """
    Response schema for project plan.

    Attributes:
        steps (List[str]): Step-by-step plan.
        bill_of_materials (Dict[str, float]): Map of product to cost.
        estimates (Dict[str, Any]): Additional estimates.
    """
    steps: List[str]
    bill_of_materials: Dict[str, float]
    estimates: Dict[str, Any]
