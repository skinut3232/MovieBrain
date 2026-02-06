interface Props {
  query: string;
  onQueryChange: (q: string) => void;
  minYear: string;
  onMinYearChange: (y: string) => void;
  maxYear: string;
  onMaxYearChange: (y: string) => void;
  genre: string;
  onGenreChange: (g: string) => void;
  minRating: string;
  onMinRatingChange: (r: string) => void;
  genres: string[];
}

export default function SearchBar({
  query,
  onQueryChange,
  minYear,
  onMinYearChange,
  maxYear,
  onMaxYearChange,
  genre,
  onGenreChange,
  minRating,
  onMinRatingChange,
  genres,
}: Props) {
  return (
    <div className="space-y-3 mb-6">
      {/* Main search input */}
      <input
        type="text"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        placeholder="Search movies..."
        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
      />

      {/* Filters row */}
      <div className="flex flex-wrap gap-3">
        <select
          value={genre}
          onChange={(e) => onGenreChange(e.target.value)}
          className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-gray-300 text-sm focus:outline-none focus:border-amber-400"
        >
          <option value="">All Genres</option>
          {genres.map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>

        <div className="flex items-center gap-2">
          <input
            type="number"
            value={minYear}
            onChange={(e) => onMinYearChange(e.target.value)}
            placeholder="From"
            className="w-20 bg-gray-800 border border-gray-600 rounded px-2 py-2 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400"
          />
          <span className="text-gray-500">-</span>
          <input
            type="number"
            value={maxYear}
            onChange={(e) => onMaxYearChange(e.target.value)}
            placeholder="To"
            className="w-20 bg-gray-800 border border-gray-600 rounded px-2 py-2 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400"
          />
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Min Rating:</label>
          <input
            type="number"
            value={minRating}
            onChange={(e) => onMinRatingChange(e.target.value)}
            placeholder="0"
            min="0"
            max="10"
            step="0.5"
            className="w-16 bg-gray-800 border border-gray-600 rounded px-2 py-2 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400"
          />
        </div>
      </div>
    </div>
  );
}
