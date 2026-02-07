"""add_omdb_rating_columns

Revision ID: b8e6f2a13d37
Revises: a7d5e1f02c26
Create Date: 2026-02-07 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8e6f2a13d37'
down_revision: Union[str, Sequence[str], None] = 'a7d5e1f02c26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('catalog_ratings', sa.Column('rt_critic_score', sa.Integer(), nullable=True))
    op.add_column('catalog_ratings', sa.Column('rt_audience_score', sa.Integer(), nullable=True))
    op.add_column('catalog_ratings', sa.Column('metacritic_score', sa.Integer(), nullable=True))
    op.add_column('catalog_ratings', sa.Column('omdb_fetched_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('catalog_ratings', 'omdb_fetched_at')
    op.drop_column('catalog_ratings', 'metacritic_score')
    op.drop_column('catalog_ratings', 'rt_audience_score')
    op.drop_column('catalog_ratings', 'rt_critic_score')
