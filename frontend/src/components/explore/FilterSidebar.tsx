import { useCallback, useEffect, useState } from 'react';
import { getLanguages, getProviders } from '../../api/catalog';
import { useDebounce } from '../../hooks/useDebounce';
import type { FilterUpdates, FilterState } from '../../hooks/useFilterParams';
import type { LanguageOption, ProviderMaster, SortOption } from '../../types';
import { getLanguageName } from '../../utils/languageCodes';

const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w92';

const ALL_GENRES = [
  'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
  'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History',
  'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
  'Sport', 'Thriller', 'War', 'Western',
];

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'popularity', label: 'Most Popular' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'year_desc', label: 'Newest First' },
  { value: 'year_asc', label: 'Oldest First' },
];

interface Props {
  filters: FilterState;
  onFilterChange: (updates: FilterUpdates) => void;
  onClearAll: () => void;
  activeFilterCount: number;
}

function FilterSection({
  title,
  defaultOpen = false,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-gray-700 pb-3 mb-3">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-200 hover:text-white"
      >
        {title}
        <svg
          className={`w-4 h-4 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
}

export default function FilterSidebar({ filters, onFilterChange, onClearAll, activeFilterCount }: Props) {
  const [languages, setLanguages] = useState<LanguageOption[]>([]);
  const [languageSearch, setLanguageSearch] = useState('');
  const [providers, setProviders] = useState<ProviderMaster[]>([]);

  // Local state for debounced numeric inputs
  const [localMinYear, setLocalMinYear] = useState(filters.minYear?.toString() ?? '');
  const [localMaxYear, setLocalMaxYear] = useState(filters.maxYear?.toString() ?? '');
  const [localMinRating, setLocalMinRating] = useState(filters.minRating?.toString() ?? '');
  const [localMinRuntime, setLocalMinRuntime] = useState(filters.minRuntime?.toString() ?? '');
  const [localMaxRuntime, setLocalMaxRuntime] = useState(filters.maxRuntime?.toString() ?? '');

  const debouncedMinYear = useDebounce(localMinYear, 400);
  const debouncedMaxYear = useDebounce(localMaxYear, 400);
  const debouncedMinRating = useDebounce(localMinRating, 400);
  const debouncedMinRuntime = useDebounce(localMinRuntime, 400);
  const debouncedMaxRuntime = useDebounce(localMaxRuntime, 400);

  // Sync local state when URL changes externally
  useEffect(() => {
    setLocalMinYear(filters.minYear?.toString() ?? '');
    setLocalMaxYear(filters.maxYear?.toString() ?? '');
    setLocalMinRating(filters.minRating?.toString() ?? '');
    setLocalMinRuntime(filters.minRuntime?.toString() ?? '');
    setLocalMaxRuntime(filters.maxRuntime?.toString() ?? '');
  }, [filters.minYear, filters.maxYear, filters.minRating, filters.minRuntime, filters.maxRuntime]);

  // Push debounced values to URL
  useEffect(() => {
    const val = debouncedMinYear ? Number(debouncedMinYear) : undefined;
    if (val !== filters.minYear) onFilterChange({ minYear: val });
  }, [debouncedMinYear]);

  useEffect(() => {
    const val = debouncedMaxYear ? Number(debouncedMaxYear) : undefined;
    if (val !== filters.maxYear) onFilterChange({ maxYear: val });
  }, [debouncedMaxYear]);

  useEffect(() => {
    const val = debouncedMinRating ? Number(debouncedMinRating) : undefined;
    if (val !== filters.minRating) onFilterChange({ minRating: val });
  }, [debouncedMinRating]);

  useEffect(() => {
    const val = debouncedMinRuntime ? Number(debouncedMinRuntime) : undefined;
    if (val !== filters.minRuntime) onFilterChange({ minRuntime: val });
  }, [debouncedMinRuntime]);

  useEffect(() => {
    const val = debouncedMaxRuntime ? Number(debouncedMaxRuntime) : undefined;
    if (val !== filters.maxRuntime) onFilterChange({ maxRuntime: val });
  }, [debouncedMaxRuntime]);

  // Load languages and providers
  useEffect(() => {
    getLanguages()
      .then((data) => setLanguages(data.languages))
      .catch(console.error);
    getProviders()
      .then((data) => setProviders(data.providers))
      .catch(console.error);
  }, []);

  const toggleGenre = useCallback(
    (genre: string) => {
      const current = filters.genres;
      const updated = current.includes(genre)
        ? current.filter((g) => g !== genre)
        : [...current, genre];
      onFilterChange({ genres: updated });
    },
    [filters.genres, onFilterChange]
  );

  const toggleProvider = useCallback(
    (providerId: number) => {
      const current = filters.providerIds;
      const updated = current.includes(providerId)
        ? current.filter((id) => id !== providerId)
        : [...current, providerId];
      onFilterChange({ providerIds: updated });
    },
    [filters.providerIds, onFilterChange]
  );

  const filteredLanguages = languages.filter((lang) => {
    if (!languageSearch) return true;
    const name = getLanguageName(lang.code).toLowerCase();
    return name.includes(languageSearch.toLowerCase()) || lang.code.includes(languageSearch.toLowerCase());
  });

  return (
    <div className="space-y-1">
      {/* Clear All */}
      {activeFilterCount > 0 && (
        <button
          onClick={onClearAll}
          className="w-full text-sm text-amber-400 hover:text-amber-300 mb-3 text-left"
        >
          Clear all filters ({activeFilterCount})
        </button>
      )}

      {/* Genre */}
      <FilterSection title="Genre" defaultOpen>
        <div className="flex flex-wrap gap-1.5">
          {ALL_GENRES.map((genre) => (
            <button
              key={genre}
              onClick={() => toggleGenre(genre)}
              className={`px-2.5 py-1 rounded-full text-xs transition ${
                filters.genres.includes(genre)
                  ? 'bg-amber-500 text-black font-medium'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {genre}
            </button>
          ))}
        </div>
      </FilterSection>

      {/* Year */}
      <FilterSection title="Year">
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="From"
            value={localMinYear}
            onChange={(e) => setLocalMinYear(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-amber-500"
          />
          <span className="text-gray-500">–</span>
          <input
            type="number"
            placeholder="To"
            value={localMaxYear}
            onChange={(e) => setLocalMaxYear(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-amber-500"
          />
        </div>
      </FilterSection>

      {/* Rating */}
      <FilterSection title="Rating">
        <div className="flex items-center gap-3">
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={localMinRating || '0'}
            onChange={(e) => {
              const val = e.target.value;
              setLocalMinRating(val === '0' ? '' : val);
            }}
            className="w-full accent-amber-500"
          />
          <span className="text-sm text-gray-300 w-10 text-right">
            {localMinRating ? `${localMinRating}+` : 'Any'}
          </span>
        </div>
      </FilterSection>

      {/* Runtime */}
      <FilterSection title="Runtime">
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Min"
            value={localMinRuntime}
            onChange={(e) => setLocalMinRuntime(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-amber-500"
          />
          <span className="text-gray-500 text-xs">min</span>
          <span className="text-gray-500">–</span>
          <input
            type="number"
            placeholder="Max"
            value={localMaxRuntime}
            onChange={(e) => setLocalMaxRuntime(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-amber-500"
          />
          <span className="text-gray-500 text-xs">min</span>
        </div>
      </FilterSection>

      {/* Language */}
      <FilterSection title="Language">
        <input
          type="text"
          placeholder="Search languages..."
          value={languageSearch}
          onChange={(e) => setLanguageSearch(e.target.value)}
          className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1.5 text-sm text-gray-200 mb-2 focus:outline-none focus:border-amber-500"
        />
        <div className="max-h-40 overflow-y-auto space-y-0.5">
          {filteredLanguages.slice(0, 50).map((lang) => (
            <button
              key={lang.code}
              onClick={() => onFilterChange({ language: filters.language === lang.code ? undefined : lang.code })}
              className={`w-full text-left px-2 py-1 rounded text-xs transition flex justify-between ${
                filters.language === lang.code
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>{getLanguageName(lang.code)}</span>
              <span className="text-gray-500">{lang.count.toLocaleString()}</span>
            </button>
          ))}
        </div>
      </FilterSection>

      {/* Where to Stream — only show if there are providers with cached movies */}
      {providers.filter(p => p.movie_count && p.movie_count > 0).length > 0 && (
        <FilterSection title="Where to Stream">
          <p className="text-xs text-gray-500 mb-2">
            Based on cached data — browse movie details to expand coverage.
          </p>
          <div className="flex flex-wrap gap-1.5">
            {providers
              .filter(p => p.movie_count && p.movie_count > 0)
              .sort((a, b) => (b.movie_count ?? 0) - (a.movie_count ?? 0))
              .slice(0, 30)
              .map((p) => (
              <button
                key={p.provider_id}
                onClick={() => toggleProvider(p.provider_id)}
                title={`${p.provider_name} (${p.movie_count} movies)`}
                className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition ${
                  filters.providerIds.includes(p.provider_id)
                    ? 'bg-amber-500/20 text-amber-400 ring-1 ring-amber-500'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {p.logo_path && (
                  <img
                    src={`${TMDB_IMAGE_BASE}${p.logo_path}`}
                    alt=""
                    className="w-4 h-4 rounded"
                  />
                )}
                <span className="truncate max-w-[100px]">{p.provider_name}</span>
                <span className="text-gray-500">({p.movie_count})</span>
              </button>
            ))}
          </div>
        </FilterSection>
      )}

      {/* Sort */}
      <FilterSection title="Sort By" defaultOpen>
        <div className="space-y-1">
          {SORT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onFilterChange({ sort: opt.value })}
              className={`w-full text-left px-2 py-1.5 rounded text-xs transition ${
                filters.sort === opt.value
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </FilterSection>

      {/* Hide Watched */}
      <FilterSection title="Hide Watched" defaultOpen>
        <label className="flex items-center gap-2 cursor-pointer">
          <button
            onClick={() => onFilterChange({ hideWatched: !filters.hideWatched })}
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
          <span className="text-sm text-gray-300">Hide watched</span>
        </label>
      </FilterSection>
    </div>
  );
}
