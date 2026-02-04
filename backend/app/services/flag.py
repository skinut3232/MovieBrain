from sqlalchemy.orm import Session

from app.models.personal import FlagType, MovieFlag


def create_flag(
    db: Session, profile_id: int, title_id: int, flag_type: FlagType
) -> MovieFlag:
    """Create or update a flag (upsert on profile_id + title_id)."""
    flag = (
        db.query(MovieFlag)
        .filter(
            MovieFlag.profile_id == profile_id,
            MovieFlag.title_id == title_id,
        )
        .first()
    )
    if flag:
        flag.flag_type = flag_type
    else:
        flag = MovieFlag(
            profile_id=profile_id,
            title_id=title_id,
            flag_type=flag_type,
        )
        db.add(flag)

    db.commit()
    db.refresh(flag)
    return flag


def delete_flag(db: Session, profile_id: int, title_id: int) -> bool:
    flag = (
        db.query(MovieFlag)
        .filter(
            MovieFlag.profile_id == profile_id,
            MovieFlag.title_id == title_id,
        )
        .first()
    )
    if not flag:
        return False
    db.delete(flag)
    db.commit()
    return True


def get_flags(
    db: Session,
    profile_id: int,
    flag_type: FlagType | None = None,
) -> list[MovieFlag]:
    query = db.query(MovieFlag).filter(MovieFlag.profile_id == profile_id)
    if flag_type is not None:
        query = query.filter(MovieFlag.flag_type == flag_type)
    return query.order_by(MovieFlag.created_at.desc()).all()
