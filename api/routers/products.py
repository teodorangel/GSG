from datetime import datetime
from fastapi import APIRouter
from api.models import ProductOut, ProductListOut

router = APIRouter()

@router.get("/", response_model=ProductListOut)
async def list_products():
    """
    Stub endpoint to list products.

    Returns:
        ProductListOut: Mocked empty product list.
    """
    return ProductListOut(items=[], total=0)

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int):
    """
    Stub endpoint to retrieve a single product by ID.

    Args:
        product_id (int): The ID of the product.

    Returns:
        ProductOut: Mocked product data.
    """
    return ProductOut(
        id=product_id,
        model="MODEL123",
        name=None,
        category=None,
        price=None,
        brand=None,
        created_at=datetime.utcnow(),
    )
