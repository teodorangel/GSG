import os
import pytest
from sqlalchemy import create_engine, inspect


def test_tables_exist():
    """
    Ensure Alembic migration created the expected tables.
    """
    db_url = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/postgres'
    )
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected = [
        'products',
        'product_documents',
        'product_images',
        'videos',
    ]
    for table in expected:
        assert table in tables, f"Expected table '{table}' not found in the database."
