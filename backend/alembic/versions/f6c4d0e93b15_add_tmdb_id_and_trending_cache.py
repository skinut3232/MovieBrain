"""add_tmdb_id_and_trending_cache

Revision ID: f6c4d0e93b15
Revises: e5b3f9d82a04
Create Date: 2026-02-06 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f6c4d0e93b15'
down_revision: Union[str, Sequence[str], None] = 'e5b3f9d82a04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add tmdb_id column to catalog_titles
    op.add_column('catalog_titles', sa.Column('tmdb_id', sa.Integer(), nullable=True))
    op.create_index('ix_catalog_titles_tmdb_id', 'catalog_titles', ['tmdb_id'])

    # 2. Create trending_cache table
    op.create_table(
        'trending_cache',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tmdb_id', sa.Integer(), nullable=False),
        sa.Column('title_id', sa.Integer(), sa.ForeignKey('catalog_titles.id', ondelete='CASCADE'), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_trending_cache_fetched_at', 'trending_cache', ['fetched_at'])
    op.create_index('ix_trending_cache_title_id', 'trending_cache', ['title_id'])


def downgrade() -> None:
    op.drop_index('ix_trending_cache_title_id', table_name='trending_cache')
    op.drop_index('ix_trending_cache_fetched_at', table_name='trending_cache')
    op.drop_table('trending_cache')

    op.drop_index('ix_catalog_titles_tmdb_id', table_name='catalog_titles')
    op.drop_column('catalog_titles', 'tmdb_id')
