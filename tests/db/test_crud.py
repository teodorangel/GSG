import pytest
from sqlalchemy.exc import IntegrityError
from shared.db import (
    SessionLocal,
    engine,
    Base,
    create_product,
    get_or_create_product,
    create_document,
    create_image,
    create_video,
)

@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database session for each test that rolls back changes.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    # Rollback transaction and close session
    session.close()
    transaction.rollback()
    connection.close()

def test_create_product(db):
    """Test creating a new product."""
    product = create_product(db, model="GXP2170", name="Enterprise HD IP Phone")
    
    assert product.id is not None
    assert product.model == "GXP2170"
    assert product.name == "Enterprise HD IP Phone"
    assert product.created_at is not None
    assert product.updated_at is not None

def test_create_product_duplicate_model(db):
    """Test that creating a product with duplicate model fails."""
    create_product(db, model="GXP2170", name="First Phone")
    
    with pytest.raises(IntegrityError):
        create_product(db, model="GXP2170", name="Second Phone")

def test_get_or_create_product_new(db):
    """Test get_or_create_product with a new product."""
    product = get_or_create_product(db, model="GXP2170", name="Enterprise HD IP Phone")
    
    assert product.id is not None
    assert product.model == "GXP2170"
    assert product.name == "Enterprise HD IP Phone"

def test_get_or_create_product_existing(db):
    """Test get_or_create_product with an existing product."""
    product1 = get_or_create_product(db, model="GXP2170", name="First Name")
    product2 = get_or_create_product(db, model="GXP2170", name="Second Name")
    
    assert product1.id == product2.id
    assert product2.name == "First Name"  # Name should not be updated

def test_create_document(db):
    """Test creating a new document."""
    product = create_product(db, model="GXP2170", name="Enterprise HD IP Phone")
    doc = create_document(
        db,
        product_id=product.id,
        url="https://example.com/manual.pdf",
        content="User manual content"
    )
    
    assert doc.id is not None
    assert doc.product_id == product.id
    assert doc.url == "https://example.com/manual.pdf"
    assert doc.content == "User manual content"
    assert doc.created_at is not None
    assert doc.updated_at is not None

def test_create_image(db):
    """Test creating a new image."""
    product = create_product(db, model="GXP2170", name="Enterprise HD IP Phone")
    image = create_image(
        db,
        product_id=product.id,
        url="https://example.com/phone.jpg"
    )
    
    assert image.id is not None
    assert image.product_id == product.id
    assert image.url == "https://example.com/phone.jpg"
    assert image.created_at is not None
    assert image.updated_at is not None

def test_create_video(db):
    """Test creating a new video."""
    product = create_product(db, model="GXP2170", name="Enterprise HD IP Phone")
    video = create_video(
        db,
        product_id=product.id,
        youtube_id="abc123",
        title="Product Overview"
    )
    
    assert video.id is not None
    assert video.product_id == product.id
    assert video.youtube_id == "abc123"
    assert video.title == "Product Overview"
    assert video.created_at is not None
    assert video.updated_at is not None

def test_create_video_duplicate_youtube_id(db):
    """Test that creating a video with duplicate youtube_id fails."""
    product = create_product(db, model="GXP2170", name="Enterprise HD IP Phone")
    create_video(db, product_id=product.id, youtube_id="abc123")
    
    with pytest.raises(IntegrityError):
        create_video(db, product_id=product.id, youtube_id="abc123") 