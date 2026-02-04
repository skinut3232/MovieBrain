from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.personal import Tag, Watch


def create_or_update_watch(
    db: Session,
    profile_id: int,
    title_id: int,
    rating_1_10: int | None,
    notes: str | None,
    rewatch_count: int,
    watched_date,
    tag_names: list[str],
) -> tuple[Watch, bool]:
    """Create or update a watch. Returns (watch, is_new)."""
    watch = (
        db.query(Watch)
        .filter(Watch.profile_id == profile_id, Watch.title_id == title_id)
        .first()
    )

    is_new = watch is None
    if is_new:
        watch = Watch(profile_id=profile_id, title_id=title_id)
        db.add(watch)

    watch.rating_1_10 = rating_1_10
    watch.notes = notes
    watch.rewatch_count = rewatch_count
    watch.watched_date = watched_date

    # Handle tags
    tags = _resolve_tags(db, profile_id, tag_names)
    watch.tags = tags

    db.commit()
    db.refresh(watch)
    return watch, is_new


def update_watch(
    db: Session,
    watch: Watch,
    rating_1_10: int | None = None,
    notes: str | None = None,
    rewatch_count: int | None = None,
    watched_date=None,
    tag_names: list[str] | None = None,
) -> Watch:
    """Partially update an existing watch."""
    if rating_1_10 is not None:
        watch.rating_1_10 = rating_1_10
    if notes is not None:
        watch.notes = notes
    if rewatch_count is not None:
        watch.rewatch_count = rewatch_count
    if watched_date is not None:
        watch.watched_date = watched_date
    if tag_names is not None:
        watch.tags = _resolve_tags(db, watch.profile_id, tag_names)

    db.commit()
    db.refresh(watch)
    return watch


def get_watch_history(
    db: Session,
    profile_id: int,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "watched_date",
    tag: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
) -> tuple[list[Watch], int]:
    base = (
        db.query(Watch)
        .options(joinedload(Watch.title), joinedload(Watch.tags))
        .filter(Watch.profile_id == profile_id)
    )

    if tag:
        base = base.join(Watch.tags).filter(Tag.name == tag)

    if min_rating is not None:
        base = base.filter(Watch.rating_1_10 >= min_rating)
    if max_rating is not None:
        base = base.filter(Watch.rating_1_10 <= max_rating)

    total = base.count()

    sort_column = {
        "watched_date": Watch.watched_date.desc().nulls_last(),
        "rating": Watch.rating_1_10.desc().nulls_last(),
        "created_at": Watch.created_at.desc(),
    }.get(sort_by, Watch.watched_date.desc().nulls_last())

    results = (
        base.order_by(sort_column)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # Deduplicate results that may arise from joinedload
    seen = set()
    unique_results = []
    for w in results:
        if w.id not in seen:
            seen.add(w.id)
            unique_results.append(w)

    return unique_results, total


def get_watch_by_title(db: Session, profile_id: int, title_id: int) -> Watch | None:
    return (
        db.query(Watch)
        .options(joinedload(Watch.title), joinedload(Watch.tags))
        .filter(Watch.profile_id == profile_id, Watch.title_id == title_id)
        .first()
    )


def delete_watch(db: Session, watch: Watch) -> None:
    db.delete(watch)
    db.commit()


def get_profile_tags(db: Session, profile_id: int) -> list[Tag]:
    return db.query(Tag).filter(Tag.profile_id == profile_id).order_by(Tag.name).all()


def create_tag(db: Session, profile_id: int, name: str) -> Tag:
    tag = Tag(profile_id=profile_id, name=name.strip())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: Tag) -> None:
    db.delete(tag)
    db.commit()


def _resolve_tags(db: Session, profile_id: int, tag_names: list[str]) -> list[Tag]:
    """Find or create tags by name for a given profile."""
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        tag = (
            db.query(Tag)
            .filter(Tag.profile_id == profile_id, Tag.name == name)
            .first()
        )
        if not tag:
            tag = Tag(profile_id=profile_id, name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags
