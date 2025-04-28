from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

# Database URL should be configured via environment variable
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/gsg"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    documents: Mapped[list["Document"]] = relationship(back_populates="product")
    images: Mapped[list["Image"]] = relationship(back_populates="product")
    videos: Mapped[list["Video"]] = relationship(back_populates="product")

class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String(1024))
    content: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationship
    product: Mapped[Product] = relationship(back_populates="documents")

class Image(Base):
    __tablename__ = "images"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationship
    product: Mapped[Product] = relationship(back_populates="images")

class Video(Base):
    __tablename__ = "videos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    youtube_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationship
    product: Mapped[Product] = relationship(back_populates="videos")

# CRUD Operations
def create_product(db: SessionLocal, *, model: str, name: str) -> Product:
    """Create a new product."""
    product = Product(model=model, name=name)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_or_create_product(db: SessionLocal, *, model: str, name: str) -> Product:
    """Get or create a product with SELECT FOR UPDATE to handle concurrency."""
    try:
        # Try to get existing product
        product = db.query(Product).filter(Product.model == model).first()
        if product:
            return product

        # Product doesn't exist, create it
        product = Product(model=model, name=name)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        # If we got an integrity error, try one more time to get the product
        return db.query(Product).filter(Product.model == model).first()

def create_document(
    db: SessionLocal, *, product_id: int, url: str, content: Optional[str] = None
) -> Document:
    """Create a new document."""
    document = Document(product_id=product_id, url=url, content=content)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def create_image(db: SessionLocal, *, product_id: int, url: str) -> Image:
    """Create a new image."""
    image = Image(product_id=product_id, url=url)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def create_video(
    db: SessionLocal, *, product_id: int, youtube_id: str, title: Optional[str] = None
) -> Video:
    """Create a new video."""
    video = Video(product_id=product_id, youtube_id=youtube_id, title=title)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video