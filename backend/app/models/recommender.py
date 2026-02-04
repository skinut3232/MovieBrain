from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.database import Base


class MovieEmbedding(Base):
    __tablename__ = "movie_embeddings"

    title_id = Column(
        Integer, ForeignKey("catalog_titles.id"), primary_key=True
    )
    model_id = Column(String(128), primary_key=True)
    embedding = Column(Vector(1536))
    embedding_text = Column(Text)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ProfileTaste(Base):
    __tablename__ = "profile_taste"

    profile_id = Column(
        Integer, ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True
    )
    model_id = Column(String(128), primary_key=True)
    taste_vector = Column(Vector(1536))
    num_rated_movies = Column(Integer, default=0)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
