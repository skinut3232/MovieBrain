"""add_poster_path_onboarding

Revision ID: d4a2b7c91e03
Revises: c3a1e5f29d01
Create Date: 2026-02-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4a2b7c91e03'
down_revision: Union[str, Sequence[str], None] = 'c3a1e5f29d01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add poster_path to catalog_titles
    op.add_column('catalog_titles', sa.Column('poster_path', sa.String(255), nullable=True))

    # Add onboarding_completed to profiles
    op.add_column('profiles', sa.Column('onboarding_completed', sa.Boolean(), server_default=sa.text('false'), nullable=False))

    # Create onboarding_movies table
    op.create_table(
        'onboarding_movies',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title_id', sa.Integer(), sa.ForeignKey('catalog_titles.id'), nullable=False, unique=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
    )
    op.create_index('ix_onboarding_movies_display_order', 'onboarding_movies', ['display_order'])


def downgrade() -> None:
    op.drop_index('ix_onboarding_movies_display_order', table_name='onboarding_movies')
    op.drop_table('onboarding_movies')
    op.drop_column('profiles', 'onboarding_completed')
    op.drop_column('catalog_titles', 'poster_path')
