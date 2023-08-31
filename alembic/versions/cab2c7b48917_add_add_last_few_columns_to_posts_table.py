"""Add add last few columns to posts table.

Revision ID: cab2c7b48917
Revises: 8bed69890a5c
Create Date: 2023-08-31 13:33:23.198495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cab2c7b48917'
down_revision: Union[str, None] = '8bed69890a5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('published', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('posts', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('Now()')))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'created_at')
    op.drop_column('posts', 'published')
    pass
