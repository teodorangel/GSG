from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from shared.db import SessionLocal, Product, Document
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])

IMAGES_BASE_URL = os.environ.get("IMAGES_BASE_URL", "/static/images/")
DOCUMENTS_BASE_URL = os.environ.get("DOCUMENTS_BASE_URL", "/static/documents/")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/products")
def get_products(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
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
                "images": [f"{IMAGES_BASE_URL}{img.url}" for img in p.images],
            }
            for p in products
        ],
        "total": total
    }

@router.get("/documents")
def get_documents(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.query(Document).count()
    docs = db.query(Document).offset(offset).limit(limit).all()
    items = []
    for d in docs:
        try:
            if d.url:
                items.append({
                    "id": d.id,
                    "url": f"{DOCUMENTS_BASE_URL}{d.url}",
                    "product_id": d.product_id,
                })
        except Exception as e:
            # Optionally log the error here
            continue
    return {
        "items": items,
        "total": total
    } 