"""add_discovery_metadata_tables

Revision ID: e5b3f9d82a04
Revises: d4a2b7c91e03
Create Date: 2026-02-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = 'e5b3f9d82a04'
down_revision: Union[str, Sequence[str], None] = 'd4a2b7c91e03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add skipped_onboarding_movies table for persisting skip state
    op.create_table(
        'skipped_onboarding_movies',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('profile_id', sa.Integer(), sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title_id', sa.Integer(), sa.ForeignKey('catalog_titles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('profile_id', 'title_id', name='uq_skipped_onboarding_profile_title'),
    )
    op.create_index('ix_skipped_onboarding_movies_profile_id', 'skipped_onboarding_movies', ['profile_id'])

    # 2. Add overview and trailer_key to catalog_titles
    op.add_column('catalog_titles', sa.Column('overview', sa.Text(), nullable=True))
    op.add_column('catalog_titles', sa.Column('trailer_key', sa.String(20), nullable=True))

    # 3. Create collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('collection_type', sa.String(20), nullable=False),  # 'curated' or 'auto'
        sa.Column('query_params', JSONB(), nullable=True),  # For auto collections
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_collections_collection_type', 'collections', ['collection_type'])

    # 4. Create collection_items table for curated collections
    op.create_table(
        'collection_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title_id', sa.Integer(), sa.ForeignKey('catalog_titles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('collection_id', 'title_id', name='uq_collection_item_collection_title'),
    )
    op.create_index('ix_collection_items_collection_id', 'collection_items', ['collection_id'])
    op.create_index('ix_collection_items_title_id', 'collection_items', ['title_id'])


def downgrade() -> None:
    op.drop_index('ix_collection_items_title_id', table_name='collection_items')
    op.drop_index('ix_collection_items_collection_id', table_name='collection_items')
    op.drop_table('collection_items')

    op.drop_index('ix_collections_collection_type', table_name='collections')
    op.drop_table('collections')

    op.drop_column('catalog_titles', 'trailer_key')
    op.drop_column('catalog_titles', 'overview')

    op.drop_index('ix_skipped_onboarding_movies_profile_id', table_name='skipped_onboarding_movies')
    op.drop_table('skipped_onboarding_movies')
