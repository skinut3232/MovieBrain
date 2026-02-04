interface Props {
  query: string;
  onQueryChange: (q: string) => void;
  year: string;
  onYearChange: (y: string) => void;
}

export default function SearchBar({
  query,
  onQueryChange,
  year,
  onYearChange,
}: Props) {
  return (
    <div className="flex gap-3 mb-6">
      <input
        type="text"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        placeholder="Search movies..."
        className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
      />
      <input
        type="number"
        value={year}
        onChange={(e) => onYearChange(e.target.value)}
        placeholder="Year"
        className="w-24 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
      />
    </div>
  );
}
