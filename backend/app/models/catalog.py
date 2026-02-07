from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CatalogTitle(Base):
    __tablename__ = "catalog_titles"

    id = Column(Integer, primary_key=True, index=True)
    imdb_tconst = Column(String(20), unique=True, nullable=False, index=True)
    tmdb_id = Column(Integer, index=True)
    title_type = Column(String(50))
    primary_title = Column(String(500), nullable=False)
    original_title = Column(String(500))
    start_year = Column(Integer)
    end_year = Column(Integer)
    runtime_minutes = Column(Integer)
    genres = Column(String(200))
    poster_path = Column(String(255))
    overview = Column(Text)
    trailer_key = Column(String(20))
    title_search_text = Column(Text)
    ts_vector = Column(TSVECTOR)

    rating = relationship("CatalogRating", back_populates="title", uselist=False)
    principals = relationship("CatalogPrincipal", back_populates="title")
    crew = relationship("CatalogCrew", back_populates="title", uselist=False)
    akas = relationship("CatalogAka", back_populates="title")

    @property
    def poster_url(self) -> str | None:
        if not self.poster_path:
            return None
        from app.config import settings
        return f"{settings.TMDB_IMAGE_BASE_URL}w300{self.poster_path}"

    __table_args__ = (
        Index("ix_catalog_titles_ts_vector", "ts_vector", postgresql_using="gin"),
        Index("ix_catalog_titles_start_year", "start_year"),
        Index("ix_catalog_titles_genres", "genres"),
    )


class CatalogRating(Base):
    __tablename__ = "catalog_ratings"

    id = Column(Integer, primary_key=True, index=True)
    title_id = Column(Integer, ForeignKey("catalog_titles.id"), nullable=False, unique=True)
    average_rating = Column(Float)
    num_votes = Column(Integer)

    title = relationship("CatalogTitle", back_populates="rating")


class CatalogPerson(Base):
    __tablename__ = "catalog_people"

    id = Column(Integer, primary_key=True, index=True)
    imdb_nconst = Column(String(20), unique=True, nullable=False, index=True)
    primary_name = Column(String(300), nullable=False)
    birth_year = Column(Integer)
    death_year = Column(Integer)

    principals = relationship("CatalogPrincipal", back_populates="person")


class CatalogPrincipal(Base):
    __tablename__ = "catalog_principals"

    id = Column(Integer, primary_key=True, index=True)
    title_id = Column(Integer, ForeignKey("catalog_titles.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("catalog_people.id"), nullable=False)
    ordering = Column(Integer)
    category = Column(String(100))
    job = Column(Text)
    characters = Column(Text)

    title = relationship("CatalogTitle", back_populates="principals")
    person = relationship("CatalogPerson", back_populates="principals")

    __table_args__ = (
        Index("ix_catalog_principals_title_id", "title_id"),
        Index("ix_catalog_principals_person_id", "person_id"),
    )


class CatalogCrew(Base):
    __tablename__ = "catalog_crew"

    id = Column(Integer, primary_key=True, index=True)
    title_id = Column(Integer, ForeignKey("catalog_titles.id"), nullable=False, unique=True)
    director_nconsts = Column(ARRAY(String))
    writer_nconsts = Column(ARRAY(String))

    title = relationship("CatalogTitle", back_populates="crew")


class CatalogAka(Base):
    __tablename__ = "catalog_akas"

    id = Column(Integer, primary_key=True, index=True)
    title_id = Column(Integer, ForeignKey("catalog_titles.id"), nullable=False)
    ordering = Column(Integer)
    localized_title = Column(String(1000))
    region = Column(String(10))
    language = Column(String(10))
    is_original = Column(Boolean, default=False)

    title = relationship("CatalogTitle", back_populates="akas")

    __table_args__ = (
        Index("ix_catalog_akas_title_id", "title_id"),
        Index("ix_catalog_akas_language", "language"),
    )


class ProviderMaster(Base):
    __tablename__ = "provider_master"

    provider_id = Column(Integer, primary_key=True, autoincrement=False)
    provider_name = Column(String(200), nullable=False)
    logo_path = Column(String(255))
    display_priority = Column(Integer)


class WatchProvider(Base):
    __tablename__ = "watch_providers"

    id = Column(Integer, primary_key=True, index=True)
    title_id = Column(Integer, ForeignKey("catalog_titles.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, nullable=False)
    provider_name = Column(String(200), nullable=False)
    logo_path = Column(String(255))
    provider_type = Column(String(20), nullable=False)  # flatrate, rent, buy
    region = Column(String(10), nullable=False, server_default="US")
    display_priority = Column(Integer)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    title = relationship("CatalogTitle")

    __table_args__ = (
        Index("ix_watch_providers_title_id", "title_id"),
        Index("ix_watch_providers_provider_id", "provider_id"),
        Index("ix_watch_providers_region", "region"),
    )


class TrendingCache(Base):
    __tablename__ = "trending_cache"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, nullable=False)
    title_id = Column(Integer, ForeignKey("catalog_titles.id", ondelete="CASCADE"), nullable=True)
    rank = Column(Integer, nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    title = relationship("CatalogTitle")

    __table_args__ = (
        Index("ix_trending_cache_fetched_at", "fetched_at"),
        Index("ix_trending_cache_title_id", "title_id"),
    )
