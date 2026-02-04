from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import CatalogPrincipal, CatalogRating, CatalogTitle


def search_titles(
    db: Session,
    query: str,
    year: int | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list, int]:
    ts_query = func.plainto_tsquery("english", query)

    base = (
        db.query(CatalogTitle)
        .outerjoin(CatalogRating, CatalogTitle.id == CatalogRating.title_id)
        .filter(CatalogTitle.ts_vector.op("@@")(ts_query))
    )

    if year is not None:
        base = base.filter(CatalogTitle.start_year == year)

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
