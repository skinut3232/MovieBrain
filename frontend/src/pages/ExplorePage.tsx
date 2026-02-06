import { useCallback, useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  browseCatalog,
  getCollections,
  getDecades,
  getGenres,
} from '../api/catalog';
import type { BrowseFilters } from '../api/catalog';
import MovieGrid from '../components/common/MovieGrid';
import type { BrowseTitle, CollectionBrief, SortOption } from '../types';

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'popularity', label: 'Most Popular' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'year_desc', label: 'Newest First' },
  { value: 'year_asc', label: 'Oldest First' },
];

export default function ExplorePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [movies, setMovies] = useState<BrowseTitle[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [genres, setGenres] = useState<string[]>([]);
  const [decades, setDecades] = useState<number[]>([]);
  const [collections, setCollections] = useState<CollectionBrief[]>([]);

  // Filters from URL
  const selectedGenre = searchParams.get('genre') || '';
  const selectedDecade = searchParams.get('decade') ? Number(searchParams.get('decade')) : undefined;
  const sortBy = (searchParams.get('sort') as SortOption) || 'popularity';

  useEffect(() => {
    Promise.all([getGenres(), getDecades(), getCollections()])
      .then(([g, d, c]) => {
        setGenres(g);
        setDecades(d);
        setCollections(c);
      })
      .catch(console.error);
  }, []);

  const loadMovies = useCallback(async () => {
    setLoading(true);
    try {
      const filters: BrowseFilters = {
        genre: selectedGenre || undefined,
        decade: selectedDecade,
        sortBy,
      };
      const data = await browseCatalog(page, 24, filters);
      setMovies(data.results);
      setTotal(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedGenre, selectedDecade, sortBy, page]);

  useEffect(() => {
    loadMovies();
  }, [loadMovies]);

  const updateFilter = (key: string, value: string | number | undefined) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, String(value));
    } else {
      params.delete(key);
    }
    // Reset to page 1 when filter changes
    setPage(1);
    setSearchParams(params);
  };

  const clearFilters = () => {
    setPage(1);
    setSearchParams({});
  };

  const totalPages = Math.ceil(total / 24);
  const hasFilters = selectedGenre || selectedDecade;

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Explore Movies</h1>

      {/* Collections Section */}
      {collections.length > 0 && !hasFilters && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-200 mb-3">Collections</h2>
          <div className="flex flex-wrap gap-2">
            {collections.map((c) => (
              <Link
                key={c.id}
                to={`/collections/${c.id}`}
                className="px-4 py-2 bg-gray-800 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition"
              >
                {c.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Genre Chips */}
      <div className="mb-4">
        <h2 className="text-sm font-medium text-gray-400 mb-2">Genres</h2>
        <div className="flex flex-wrap gap-2">
          {genres.map((g) => (
            <button
              key={g}
              onClick={() => updateFilter('genre', g === selectedGenre ? undefined : g)}
              className={`px-3 py-1 rounded-full text-sm transition ${
                g === selectedGenre
                  ? 'bg-amber-500 text-black font-medium'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* Decade Chips */}
      <div className="mb-4">
        <h2 className="text-sm font-medium text-gray-400 mb-2">Decades</h2>
        <div className="flex flex-wrap gap-2">
          {decades.map((d) => (
            <button
              key={d}
              onClick={() => updateFilter('decade', d === selectedDecade ? undefined : d)}
              className={`px-3 py-1 rounded-full text-sm transition ${
                d === selectedDecade
                  ? 'bg-amber-500 text-black font-medium'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {d}s
            </button>
          ))}
        </div>
      </div>

      {/* Sort & Clear Filters */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <select
            value={sortBy}
            onChange={(e) => updateFilter('sort', e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-300 text-sm focus:outline-none focus:border-amber-500"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-gray-400 hover:text-white"
            >
              Clear filters
            </button>
          )}
        </div>
        <span className="text-sm text-gray-400">
          {total.toLocaleString()} movies
        </span>
      </div>

      {/* Results Grid */}
      {loading ? (
        <p className="text-gray-400 text-center py-8">Loading...</p>
      ) : movies.length === 0 ? (
        <p className="text-gray-400 text-center py-8">No movies found with these filters.</p>
      ) : (
        <>
          <MovieGrid
            movies={movies.map((m) => ({
              id: m.id,
              primary_title: m.primary_title,
              start_year: m.start_year,
              genres: m.genres,
              average_rating: m.average_rating,
              num_votes: m.num_votes,
              poster_url: m.poster_url,
            }))}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-gray-400 px-4">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
