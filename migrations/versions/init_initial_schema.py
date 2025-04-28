"""initial schema

Revision ID: init
Revises: 
Create Date: 2025-04-28 07:23:30.100606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'init'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('model', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    # Create product_documents table
    op.create_table(
        'product_documents',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=False),
        sa.Column('doc_type', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('file_path', sa.String(length=512), nullable=True),
        sa.Column('url', sa.String(length=512), nullable=True),
    )
    # Create product_images table
    op.create_table(
        'product_images',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=False),
        sa.Column('image_type', sa.String(length=50), nullable=True),
        sa.Column('path', sa.String(length=512), nullable=True),
    )
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=False),
        sa.Column('youtube_id', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('videos')
    op.drop_table('product_images')
    op.drop_table('product_documents')
    op.drop_table('products')
