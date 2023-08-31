"""Create userss table.

Revision ID: 61fea0cf3445
Revises: 6465abb79a7c
Create Date: 2023-08-31 12:57:52.618800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61fea0cf3445'
down_revision: Union[str, None] = '6465abb79a7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
