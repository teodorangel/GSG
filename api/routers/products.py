from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from api.models import ProductOut, ProductListOut
from sqlalchemy.orm import Session
from sqlalchemy import func
from shared.db import Product, Image
from api.deps import get_db
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
def get_products(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.query(Product).count()
    products = db.query(Product).offset(offset).limit(limit).all()
    return {
        "items": [
            {
                "id": p.id,
                "model": p.model,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "brand": p.brand,
                "created_at": p.created_at,
                "images": [img.url for img in p.images],
                "documents": [doc.url for doc in p.documents],
            }
            for p in products
        ],
        "total": total
    }

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Stub endpoint to retrieve a single product by ID.

    Args:
        product_id (int): The ID of the product.

    Returns:
        ProductOut: Mocked product data.
    """
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    # Build dict for Pydantic
    return {
        "id": p.id,
        "model": p.model,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "brand": p.brand,
        "created_at": p.created_at,
        "images": [img.url for img in p.images],
        "documents": [doc.url for doc in p.documents],
    }

@router.post("/cleanup")
async def cleanup_images(db: Session = Depends(get_db)):
    """Remove duplicate images for each product (same product_id, url)."""
    removed = 0
    for product in db.query(Product).all():
        seen = set()
        for img in list(product.images):
            key = (img.url,)
            if key in seen:
                db.delete(img)
                removed += 1
            else:
                seen.add(key)
    db.commit()
    return JSONResponse({"removed": removed, "status": "ok"})
