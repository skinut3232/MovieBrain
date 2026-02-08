import { useEffect, useState } from 'react';
import { getGenres, searchTitles } from '../api/catalog';
import type { SearchFilters } from '../api/catalog';
import SearchBar from '../components/catalog/SearchBar';
import SearchResults from '../components/catalog/SearchResults';
import { useDebounce } from '../hooks/useDebounce';
import type { PaginatedSearchResponse } from '../types';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [minYear, setMinYear] = useState('');
  const [maxYear, setMaxYear] = useState('');
  const [genre, setGenre] = useState('');
  const [minRating, setMinRating] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PaginatedSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [genres, setGenres] = useState<string[]>([]);

  const debouncedQuery = useDebounce(query, 400);

  // Load genres on mount
  useEffect(() => {
    getGenres().then(setGenres).catch(console.error);
  }, []);

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setData(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    const filters: SearchFilters = {};
    if (genre) filters.genre = genre;
    if (minYear) filters.minYear = Number(minYear);
    if (maxYear) filters.maxYear = Number(maxYear);
    if (minRating) filters.minRating = Number(minRating);

    searchTitles(debouncedQuery, page, filters)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) console.error('Search failed:', err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [debouncedQuery, page, genre, minYear, maxYear, minRating]);

  useEffect(() => {
    setPage(1);
  }, [debouncedQuery, genre, minYear, maxYear, minRating]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Search Movies</h1>
      <SearchBar
        query={query}
        onQueryChange={setQuery}
        minYear={minYear}
        onMinYearChange={setMinYear}
        maxYear={maxYear}
        onMaxYearChange={setMaxYear}
        genre={genre}
        onGenreChange={setGenre}
        minRating={minRating}
        onMinRatingChange={setMinRating}
        genres={genres}
      />
      {loading && <p className="text-gray-400">Searching...</p>}
      {data && !loading && (
        <SearchResults data={data} page={page} onPageChange={setPage} />
      )}
      {!data && !loading && debouncedQuery && (
        <p className="text-gray-500">No results.</p>
      )}
    </div>
  );
}
