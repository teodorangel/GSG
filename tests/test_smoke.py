"""
Smoke test – verifies core deps are importable and env config is present.
Run with:  pytest -q
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def test_imports():
    """Scrapy and psycopg should import without error."""
    import scrapy  # noqa: F401
    import psycopg  # noqa: F401

    # If versions aren't critical you can just assert they exist
    assert scrapy.__version__
    assert psycopg.__version__


def test_env_vars():
    """Required env vars should be defined (even if blank in CI)."""
    required = ["DATABASE_URL", "OPENAI_API_KEY"]
    missing = [var for var in required if var not in os.environ]
    assert not missing, f"Missing env vars: {missing}" 