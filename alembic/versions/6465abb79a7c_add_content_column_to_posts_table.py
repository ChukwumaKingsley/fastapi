"""Add content column to  posts table.

Revision ID: 6465abb79a7c
Revises: db0afc6a2a36
Create Date: 2023-08-31 09:52:09.181727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6465abb79a7c'
down_revision: Union[str, None] = 'db0afc6a2a36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass