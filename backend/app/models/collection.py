from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    collection_type = Column(String(20), nullable=False)  # 'curated' or 'auto'
    query_params = Column(JSONB, nullable=True)  # For auto collections
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items = relationship("CollectionItem", back_populates="collection", cascade="all, delete-orphan")


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    title_id = Column(Integer, ForeignKey("catalog_titles.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    collection = relationship("Collection", back_populates="items")
    title = relationship("CatalogTitle")
