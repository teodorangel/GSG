import os
import pytest
from sqlalchemy import create_engine, inspect, text
from alembic.config import Config
from alembic import command


def test_tables_exist():
    """
    Ensure Alembic migration created the expected tables.
    """
    db_url = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/gsg'
    )
    # Reset schema to ensure clean database
    reset_engine = create_engine(db_url)
    # Use autocommit for DDL statements
    with reset_engine.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
        connection.execute(text('DROP SCHEMA IF EXISTS public CASCADE'))
        connection.execute(text('CREATE SCHEMA public'))
    reset_engine.dispose()
    # Apply Alembic migrations
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    alembic_cfg = Config(os.path.join(project_root, 'alembic.ini'))
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)
    command.upgrade(alembic_cfg, 'head')
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected = [
        'products',
        'documents',
        'images',
        'videos',
        'alembic_version'
    ]
    for table in expected:
        assert table in tables, f"Expected table '{table}' not found in the database."
