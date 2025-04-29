from typing import List, Optional
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
