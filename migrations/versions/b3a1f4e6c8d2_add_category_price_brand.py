"""add category, price, and brand columns to products table

Revision ID: b3a1f4e6c8d2
Revises: 8f280439b791
Create Date: 2024-06-12 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b3a1f4e6c8d2'
down_revision: Union[str, None] = '8f280439b791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new optional fields to products."""
    op.add_column('products', sa.Column('category', sa.String(length=255), nullable=True))
    op.add_column('products', sa.Column('price', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('brand', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove added fields from products."""
    op.drop_column('products', 'brand')
    op.drop_column('products', 'price')
    op.drop_column('products', 'category') 