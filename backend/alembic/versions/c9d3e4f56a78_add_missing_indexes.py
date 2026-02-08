"""add_missing_indexes

Revision ID: c9d3e4f56a78
Revises: b8e6f2a13d37
Create Date: 2026-02-07 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9d3e4f56a78"
down_revision: Union[str, None] = "b8e6f2a13d37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Performance-critical indexes identified in audit

    # catalog_ratings: used in sort and filter on almost every browse query
    op.create_index("ix_catalog_ratings_average_rating", "catalog_ratings", ["average_rating"])
    op.create_index("ix_catalog_ratings_num_votes", "catalog_ratings", ["num_votes"])

    # profiles: every profile lookup filters by user_id
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"])

    # lists: every list query filters by profile_id
    op.create_index("ix_lists_profile_id", "lists", ["profile_id"])

    # watches: default sort column for watch history
    op.create_index("ix_watches_watched_date", "watches", ["watched_date"])

    # catalog_titles: runtime filter used in browse
    op.create_index("ix_catalog_titles_runtime_minutes", "catalog_titles", ["runtime_minutes"])


def downgrade() -> None:
    op.drop_index("ix_catalog_titles_runtime_minutes", table_name="catalog_titles")
    op.drop_index("ix_watches_watched_date", table_name="watches")
    op.drop_index("ix_lists_profile_id", table_name="lists")
    op.drop_index("ix_profiles_user_id", table_name="profiles")
    op.drop_index("ix_catalog_ratings_num_votes", table_name="catalog_ratings")
    op.drop_index("ix_catalog_ratings_average_rating", table_name="catalog_ratings")
