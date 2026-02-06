from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class OnboardingMovie(Base):
    __tablename__ = "onboarding_movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title_id = Column(Integer, ForeignKey("catalog_titles.id"), nullable=False, unique=True)
    display_order = Column(Integer, nullable=False)

    title = relationship("CatalogTitle")


class SkippedOnboardingMovie(Base):
    __tablename__ = "skipped_onboarding_movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    title_id = Column(Integer, ForeignKey("catalog_titles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    profile = relationship("Profile")
    title = relationship("CatalogTitle")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    onboarding_completed = Column(Boolean, server_default="false", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="profiles")
