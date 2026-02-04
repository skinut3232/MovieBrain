import enum

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Watch(Base):
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(
        Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    title_id = Column(
        Integer, ForeignKey("catalog_titles.id"), nullable=False
    )
    rating_1_10 = Column(Integer)
    notes = Column(Text)
    rewatch_count = Column(Integer, default=0)
    watched_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    profile = relationship("Profile", backref="watches")
    title = relationship("CatalogTitle")
    tags = relationship("Tag", secondary="watch_tags", back_populates="watches")

    __table_args__ = (
        UniqueConstraint("profile_id", "title_id", name="uq_watch_profile_title"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(
        Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)

    profile = relationship("Profile", backref="tags")
    watches = relationship("Watch", secondary="watch_tags", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("profile_id", "name", name="uq_tag_profile_name"),
    )


class WatchTag(Base):
    __tablename__ = "watch_tags"

    watch_id = Column(
        Integer, ForeignKey("watches.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class ListType(str, enum.Enum):
    watchlist = "watchlist"
    favorites = "favorites"
    rewatch = "rewatch"
    custom = "custom"


class MovieList(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(
        Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(200), nullable=False)
    list_type = Column(Enum(ListType), nullable=False, default=ListType.custom)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    profile = relationship("Profile", backref="lists")
    items = relationship(
        "ListItem", back_populates="movie_list", cascade="all, delete-orphan",
        order_by="ListItem.position",
    )


class ListItem(Base):
    __tablename__ = "list_items"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(
        Integer, ForeignKey("lists.id", ondelete="CASCADE"), nullable=False
    )
    title_id = Column(
        Integer, ForeignKey("catalog_titles.id"), nullable=False
    )
    position = Column(Integer, nullable=False, default=0)
    priority = Column(Integer)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    movie_list = relationship("MovieList", back_populates="items")
    title = relationship("CatalogTitle")

    __table_args__ = (
        UniqueConstraint("list_id", "title_id", name="uq_listitem_list_title"),
    )


class FlagType(str, enum.Enum):
    not_interested = "not_interested"
    dont_recommend = "dont_recommend"


class MovieFlag(Base):
    __tablename__ = "movie_flags"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(
        Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    title_id = Column(
        Integer, ForeignKey("catalog_titles.id"), nullable=False
    )
    flag_type = Column(Enum(FlagType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", backref="flags")
    title = relationship("CatalogTitle")

    __table_args__ = (
        UniqueConstraint(
            "profile_id", "title_id", name="uq_flag_profile_title"
        ),
    )
