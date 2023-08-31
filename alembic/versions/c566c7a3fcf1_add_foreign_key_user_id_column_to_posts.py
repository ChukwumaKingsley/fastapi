"""Add foreign key user id column to posts"

Revision ID: c566c7a3fcf1
Revises: 5c1307857afe
Create Date: 2023-08-31 21:32:49.452924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c566c7a3fcf1'
down_revision: Union[str, None] = '5c1307857afe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('user_id', sa.Integer()))
    op.create_foreign_key(
        'fk_posts_user_id',  # Constraint name
        'posts',             # Source table
        'users',             # Referenced table
        ['user_id'],         # Source column(s)
        ['id'],              # Referenced column(s)
        ondelete="CASCADE",
        onupdate="CASCADE"
    )
    pass


def downgrade() -> None:
    op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
    op.drop_column('posts', 'user_id')
    pass
