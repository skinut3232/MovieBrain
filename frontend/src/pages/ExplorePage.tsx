import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  browseCatalog,
  getCollections,
  getFeaturedGenres,
  getFeaturedRows,
} from '../api/catalog';
import type { BrowseFilters } from '../api/catalog';
import CollectionCard from '../components/explore/CollectionCard';
import FilterSidebar from '../components/explore/FilterSidebar';
import GenreChips from '../components/explore/GenreChips';
import MovieRow from '../components/explore/MovieRow';
import SurpriseMe from '../components/explore/SurpriseMe';
import MovieGrid from '../components/common/MovieGrid';
import { useProfile } from '../context/ProfileContext';
import { useFilterParams } from '../hooks/useFilterParams';
import type { BrowseTitle, CollectionBrief, FeaturedRow } from '../types';

const DECADES = [1970, 1980, 1990, 2000, 2010, 2020];

export default function ExplorePage() {
  const { activeProfile } = useProfile();
  const { filters, setFilters, clearAllFilters, isFilteredMode, activeFilterCount } = useFilterParams();

  const [featuredRows, setFeaturedRows] = useState<FeaturedRow[]>([]);
  const [featuredGenres, setFeaturedGenres] = useState<string[]>([]);
  const [collections, setCollections] = useState<CollectionBrief[]>([]);
  const [loading, setLoading] = useState(true);

  // Filtered mode state
  const [filteredMovies, setFilteredMovies] = useState<BrowseTitle[]>([]);
  const [filteredTotal, setFilteredTotal] = useState(0);
  const [filteredPage, setFilteredPage] = useState(1);
  const [filteredLoading, setFilteredLoading] = useState(false);

  // Mobile sidebar drawer
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // Get the profile ID to exclude if hideWatched is enabled
  const excludeProfileId = filters.hideWatched && activeProfile ? activeProfile.id : undefined;

  // Load featured content for home explore view
  useEffect(() => {
    if (isFilteredMode) return;
    if (filters.hideWatched && !activeProfile) return;

    let cancelled = false;
    setLoading(true);

    Promise.all([
      getFeaturedRows(20, excludeProfileId),
      getFeaturedGenres(),
      getCollections(),
    ])
      .then(([rowsData, genres, cols]) => {
        if (cancelled) return;
        setFeaturedRows(rowsData.rows);
        setFeaturedGenres(genres);
        setCollections(cols);
      })
      .catch(console.error)
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [isFilteredMode, excludeProfileId, filters.hideWatched, activeProfile]);

  // Load filtered movies when in filtered mode
  useEffect(() => {
    if (!isFilteredMode) return;
    if (filters.hideWatched && !activeProfile) return;

    let cancelled = false;
    setFilteredLoading(true);

    const browseFilters: BrowseFilters = {
      genres: filters.genres.length > 0 ? filters.genres : undefined,
      minYear: filters.minYear,
      maxYear: filters.maxYear,
      minRating: filters.minRating,
      minRuntime: filters.minRuntime,
      maxRuntime: filters.maxRuntime,
      language: filters.language,
      sortBy: filters.sort,
      excludeWatchedProfileId: excludeProfileId,
      providerIds: filters.providerIds.length > 0 ? filters.providerIds : undefined,
    };

    browseCatalog(filteredPage, 24, browseFilters)
      .then((data) => {
        if (cancelled) return;
        setFilteredMovies(data.results);
        setFilteredTotal(data.total);
      })
      .catch(console.error)
      .finally(() => {
        if (!cancelled) setFilteredLoading(false);
      });

    return () => { cancelled = true; };
  }, [
    filters.genres, filters.minYear, filters.maxYear, filters.minRating,
    filters.minRuntime, filters.maxRuntime, filters.language, filters.sort,
    filters.hideWatched, filters.providerIds, filters.browseAll,
    filteredPage, isFilteredMode, excludeProfileId, activeProfile,
  ]);

  // Reset page when filters change
  useEffect(() => {
    setFilteredPage(1);
  }, [
    filters.genres, filters.minYear, filters.maxYear, filters.minRating,
    filters.minRuntime, filters.maxRuntime, filters.language, filters.sort,
    filters.providerIds,
  ]);

  const totalPages = Math.ceil(filteredTotal / 24);

  // Build the filter title for browse mode
  const getFilterTitle = useCallback(() => {
    if (filters.genres.length === 1) return `${filters.genres[0]} Movies`;
    if (filters.genres.length > 1) return `${filters.genres.join(', ')} Movies`;
    if (filters.minYear && filters.maxYear && filters.maxYear - filters.minYear === 9)
      return `${filters.minYear}s Movies`;
    return 'Browse Movies';
  }, [filters.genres, filters.minYear, filters.maxYear]);

  // Filtered Mode View
  if (isFilteredMode) {
    return (
      <div className="max-w-7xl mx-auto">
        {/* Back link */}
        <div className="flex items-center gap-4 mb-6">
          <Link
            to="/explore"
            className="text-amber-400 hover:text-amber-300 flex items-center gap-1"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Explore
          </Link>
        </div>

        <h1 className="text-2xl font-bold text-white mb-4">{getFilterTitle()}</h1>

        {/* Mobile filter button */}
        <div className="lg:hidden mb-4">
          <button
            onClick={() => setMobileDrawerOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-700"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Filters
            {activeFilterCount > 0 && (
              <span className="bg-amber-500 text-black text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </button>
        </div>

        {/* Mobile drawer backdrop + sidebar */}
        {mobileDrawerOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div
              className="absolute inset-0 bg-black/60"
              onClick={() => setMobileDrawerOpen(false)}
            />
            <div className="absolute left-0 top-0 bottom-0 w-72 bg-gray-900 border-r border-gray-700 p-4 overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Filters</h2>
                <button
                  onClick={() => setMobileDrawerOpen(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <FilterSidebar
                filters={filters}
                onFilterChange={(updates) => {
                  setFilters(updates);
                }}
                onClearAll={clearAllFilters}
                activeFilterCount={activeFilterCount}
              />
            </div>
          </div>
        )}

        {/* Desktop layout: sidebar + content */}
        <div className="flex gap-6">
          {/* Desktop sidebar */}
          <aside className="hidden lg:block w-72 flex-shrink-0">
            <div className="sticky top-4">
              <FilterSidebar
                filters={filters}
                onFilterChange={setFilters}
                onClearAll={clearAllFilters}
                activeFilterCount={activeFilterCount}
              />
            </div>
          </aside>

          {/* Results area */}
          <div className="flex-1 min-w-0">
            {/* Results header */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-400">
                {filteredTotal.toLocaleString()} movies
              </span>
            </div>

            {/* Results Grid */}
            {filteredLoading ? (
              <p className="text-gray-400 text-center py-8">Loading...</p>
            ) : filteredMovies.length === 0 ? (
              <p className="text-gray-400 text-center py-8">
                No movies found with these filters.
              </p>
            ) : (
              <>
                <MovieGrid
                  movies={filteredMovies.map((m) => ({
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
                      onClick={() => setFilteredPage((p) => Math.max(1, p - 1))}
                      disabled={filteredPage === 1}
                      className="px-4 py-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="text-gray-400 px-4">
                      Page {filteredPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => setFilteredPage((p) => Math.min(totalPages, p + 1))}
                      disabled={filteredPage === totalPages}
                      className="px-4 py-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Home Explore View (Netflix-style)
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <p className="text-gray-400 text-center py-8">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Top bar: Browse All + Hide Watched */}
      <div className="flex items-center justify-between mb-4">
        <Link
          to="/explore?browse=all"
          className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          Browse All Movies
        </Link>
        <label className="flex items-center gap-2 cursor-pointer">
          <span className="text-sm text-gray-400">Hide watched movies</span>
          <button
            onClick={() => {
              const newVal = !filters.hideWatched;
              localStorage.setItem('explore_hide_watched', String(newVal));
              setFilters({ hideWatched: newVal });
            }}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              filters.hideWatched ? 'bg-amber-500' : 'bg-gray-600'
            }`}
            role="switch"
            aria-checked={filters.hideWatched}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                filters.hideWatched ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </label>
      </div>

      {/* Surprise Me Section */}
      <SurpriseMe genres={featuredGenres} excludeWatchedProfileId={excludeProfileId} />

      {/* Genre & Decade Chips */}
      <GenreChips
        genres={featuredGenres}
        decades={DECADES}
        selectedGenre={filters.genres[0]}
        selectedDecade={undefined}
      />

      {/* Featured Rows */}
      {featuredRows.map((row) => (
        <MovieRow
          key={row.id}
          title={row.title}
          movies={row.movies}
          seeAllLink={
            row.id === 'trending' || row.id === 'new-releases'
              ? undefined
              : `/explore?genres=${row.title.replace(' Movies', '')}`
          }
        />
      ))}

      {/* Collections Section */}
      {collections.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-200 mb-4">
            Collections
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {collections.map((collection) => (
              <CollectionCard key={collection.id} collection={collection} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
