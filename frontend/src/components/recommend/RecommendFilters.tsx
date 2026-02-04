import { useState } from 'react';
import type { RecommendRequest } from '../../types';

interface RecommendFiltersProps {
  onApply: (filters: RecommendRequest) => void;
  loading?: boolean;
}

export default function RecommendFilters({ onApply, loading }: RecommendFiltersProps) {
  const [expanded, setExpanded] = useState(false);
  const [genre, setGenre] = useState('');
  const [minYear, setMinYear] = useState('');
  const [maxYear, setMaxYear] = useState('');
  const [minRuntime, setMinRuntime] = useState('');
  const [maxRuntime, setMaxRuntime] = useState('');
  const [minRating, setMinRating] = useState('');

  const handleApply = () => {
    const filters: RecommendRequest = {};
    if (genre.trim()) filters.genre = genre.trim();
    if (minYear) filters.min_year = parseInt(minYear);
    if (maxYear) filters.max_year = parseInt(maxYear);
    if (minRuntime) filters.min_runtime = parseInt(minRuntime);
    if (maxRuntime) filters.max_runtime = parseInt(maxRuntime);
    if (minRating) filters.min_imdb_rating = parseFloat(minRating);
    onApply(filters);
  };

  const handleClear = () => {
    setGenre('');
    setMinYear('');
    setMaxYear('');
    setMinRuntime('');
    setMaxRuntime('');
    setMinRating('');
    onApply({});
  };

  return (
    <div className="bg-gray-900 rounded-lg border border-gray-700">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-gray-200 hover:text-white"
      >
        <span className="font-medium">Filters</span>
        <span className="text-sm text-gray-400">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Genre</label>
              <input
                type="text"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                placeholder="e.g. Action, Comedy"
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Year Range</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={minYear}
                  onChange={(e) => setMinYear(e.target.value)}
                  placeholder="From"
                  className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
                />
                <input
                  type="number"
                  value={maxYear}
                  onChange={(e) => setMaxYear(e.target.value)}
                  placeholder="To"
                  className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Runtime (min)</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={minRuntime}
                  onChange={(e) => setMinRuntime(e.target.value)}
                  placeholder="Min"
                  className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
                />
                <input
                  type="number"
                  value={maxRuntime}
                  onChange={(e) => setMaxRuntime(e.target.value)}
                  placeholder="Max"
                  className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Min IMDb Rating</label>
              <input
                type="number"
                value={minRating}
                onChange={(e) => setMinRating(e.target.value)}
                placeholder="e.g. 7.0"
                min="0"
                max="10"
                step="0.1"
                className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleApply}
              disabled={loading}
              className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold disabled:opacity-50"
            >
              Apply Filters
            </button>
            <button
              onClick={handleClear}
              disabled={loading}
              className="px-4 py-2 rounded border border-gray-600 text-gray-300 hover:text-white hover:border-gray-400 disabled:opacity-50"
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
