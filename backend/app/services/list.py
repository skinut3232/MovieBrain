from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.personal import ListItem, ListType, MovieList


def get_lists(db: Session, profile_id: int) -> list[dict]:
    """Get all lists for a profile with item counts."""
    rows = (
        db.query(MovieList, func.count(ListItem.id).label("item_count"))
        .outerjoin(ListItem, MovieList.id == ListItem.list_id)
        .filter(MovieList.profile_id == profile_id)
        .group_by(MovieList.id)
        .order_by(MovieList.created_at.desc())
        .all()
    )
    results = []
    for movie_list, item_count in rows:
        results.append({
            "id": movie_list.id,
            "name": movie_list.name,
            "list_type": movie_list.list_type,
            "created_at": movie_list.created_at,
            "updated_at": movie_list.updated_at,
            "item_count": item_count,
        })
    return results


def create_list(
    db: Session, profile_id: int, name: str, list_type: ListType
) -> MovieList:
    movie_list = MovieList(
        profile_id=profile_id, name=name, list_type=list_type
    )
    db.add(movie_list)
    db.commit()
    db.refresh(movie_list)
    return movie_list


def get_list_detail(db: Session, list_id: int) -> MovieList | None:
    return (
        db.query(MovieList)
        .options(
            joinedload(MovieList.items).joinedload(ListItem.title),
        )
        .filter(MovieList.id == list_id)
        .first()
    )


def add_list_item(
    db: Session, list_id: int, title_id: int, priority: int | None
) -> ListItem:
    # Auto-position at end
    max_pos = (
        db.query(func.max(ListItem.position))
        .filter(ListItem.list_id == list_id)
        .scalar()
    )
    position = (max_pos or 0) + 1

    item = ListItem(
        list_id=list_id,
        title_id=title_id,
        position=position,
        priority=priority,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def reorder_list_items(
    db: Session, list_id: int, ordered_title_ids: list[int]
) -> None:
    items = (
        db.query(ListItem)
        .filter(ListItem.list_id == list_id)
        .all()
    )
    title_to_item = {item.title_id: item for item in items}

    for pos, title_id in enumerate(ordered_title_ids, start=1):
        if title_id in title_to_item:
            title_to_item[title_id].position = pos

    db.commit()


def remove_list_item(db: Session, list_id: int, title_id: int) -> bool:
    item = (
        db.query(ListItem)
        .filter(ListItem.list_id == list_id, ListItem.title_id == title_id)
        .first()
    )
    if not item:
        return False

    removed_pos = item.position
    db.delete(item)

    # Recompact positions
    remaining = (
        db.query(ListItem)
        .filter(ListItem.list_id == list_id, ListItem.position > removed_pos)
        .order_by(ListItem.position)
        .all()
    )
    for ri in remaining:
        ri.position -= 1

    db.commit()
    return True


def delete_list(db: Session, movie_list: MovieList) -> None:
    db.delete(movie_list)
    db.commit()
