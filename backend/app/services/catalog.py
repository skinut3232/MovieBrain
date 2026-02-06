from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import CatalogPrincipal, CatalogRating, CatalogTitle


def search_titles(
    db: Session,
    query: str,
    year: int | None = None,
    genre: str | None = None,
    min_rating: float | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list, int]:
    ts_query = func.plainto_tsquery("english", query)

    base = (
        db.query(CatalogTitle)
        .outerjoin(CatalogRating, CatalogTitle.id == CatalogRating.title_id)
        .filter(CatalogTitle.ts_vector.op("@@")(ts_query))
    )

    # Apply exact year filter (takes precedence over min/max year)
    if year is not None:
        base = base.filter(CatalogTitle.start_year == year)
    else:
        if min_year is not None:
            base = base.filter(CatalogTitle.start_year >= min_year)
        if max_year is not None:
            base = base.filter(CatalogTitle.start_year <= max_year)

    if genre is not None:
        base = base.filter(CatalogTitle.genres.ilike(f"%{genre}%"))

    if min_rating is not None:
        base = base.filter(CatalogRating.average_rating >= min_rating)

    total = base.count()

    results = (
        base.order_by(
            func.ts_rank(CatalogTitle.ts_vector, ts_query).desc(),
            CatalogRating.num_votes.desc().nulls_last(),
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return results, total


def get_title_detail(db: Session, title_id: int) -> CatalogTitle | None:
    return (
        db.query(CatalogTitle)
        .options(
            joinedload(CatalogTitle.rating),
            joinedload(CatalogTitle.principals).joinedload(CatalogPrincipal.person),
            joinedload(CatalogTitle.crew),
            joinedload(CatalogTitle.akas),
        )
        .filter(CatalogTitle.id == title_id)
        .first()
    )
