"""create posts tables

Revision ID: 5f9af38764ef
Revises: 
Create Date: 2023-08-31 18:56:50.931202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f9af38764ef'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('posts', 
                    sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('content', sa.String(), nullable=False),
                    sa.Column('published', sa.Boolean(), nullable=False, server_default='True'),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('Now()'))
                    )
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
