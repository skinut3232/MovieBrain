from app.models.catalog import (
    CatalogAka,
    CatalogCrew,
    CatalogPerson,
    CatalogPrincipal,
    CatalogRating,
    CatalogTitle,
)
from app.models.collection import Collection, CollectionItem
from app.models.personal import (
    FlagType,
    ListItem,
    ListType,
    MovieFlag,
    MovieList,
    Tag,
    Watch,
    WatchTag,
)
from app.models.recommender import MovieEmbedding, ProfileTaste
from app.models.user import OnboardingMovie, Profile, SkippedOnboardingMovie, User

__all__ = [
    "CatalogTitle",
    "CatalogRating",
    "CatalogPerson",
    "CatalogPrincipal",
    "CatalogCrew",
    "CatalogAka",
    "User",
    "Profile",
    "Watch",
    "Tag",
    "WatchTag",
    "MovieList",
    "ListItem",
    "ListType",
    "MovieFlag",
    "FlagType",
    "MovieEmbedding",
    "ProfileTaste",
    "OnboardingMovie",
    "SkippedOnboardingMovie",
    "Collection",
    "CollectionItem",
]
