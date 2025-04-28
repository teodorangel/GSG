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
    # Remove explicit table creation calls
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('videos')
    op.drop_table('product_images')
    op.drop_table('product_documents')
    op.drop_table('products')
