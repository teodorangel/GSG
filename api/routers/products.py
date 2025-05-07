from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from api.models import ProductOut, ProductListOut
from sqlalchemy.orm import Session
from sqlalchemy import func
from shared.db import SessionLocal, Product, Image
from fastapi.responses import JSONResponse

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=ProductListOut)
async def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    List products from the database with pagination.
    """
    db_items = db.query(Product).offset(skip).limit(limit).all()
    total = db.query(func.count(Product.id)).scalar() or 0
    # Map each SQLAlchemy Product to dict for Pydantic
    items = []
    for p in db_items:
        items.append({
            "id": p.id,
            "model": p.model,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "brand": p.brand,
            "created_at": p.created_at,
            "images": [img.url for img in p.images],
            "documents": [doc.url for doc in p.documents],
        })
    return ProductListOut(items=items, total=total)

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
