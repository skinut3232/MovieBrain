def build_embedding_text(
    primary_title: str,
    start_year: int | None,
    genres: str | None,
    directors: list[str] | None = None,
    cast: list[str] | None = None,
) -> str:
    """Build a text string for embedding a movie.

    Format: "{title} ({year}). {genres}. Directed by {dirs}. Starring {cast}."
    """
    parts = []

    if start_year:
        parts.append(f"{primary_title} ({start_year})")
    else:
        parts.append(primary_title)

    if genres:
        parts.append(genres)

    if directors:
        parts.append(f"Directed by {', '.join(directors)}")

    if cast:
        parts.append(f"Starring {', '.join(cast)}")

    return ". ".join(parts) + "."
