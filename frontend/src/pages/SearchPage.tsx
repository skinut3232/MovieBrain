import { useEffect, useState } from 'react';
import { searchTitles } from '../api/catalog';
import SearchBar from '../components/catalog/SearchBar';
import SearchResults from '../components/catalog/SearchResults';
import { useDebounce } from '../hooks/useDebounce';
import type { PaginatedSearchResponse } from '../types';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [year, setYear] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PaginatedSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const debouncedQuery = useDebounce(query, 400);

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setData(null);
      return;
    }
    setLoading(true);
    searchTitles(debouncedQuery, page, year ? Number(year) : undefined)
      .then(setData)
      .finally(() => setLoading(false));
  }, [debouncedQuery, page, year]);

  useEffect(() => {
    setPage(1);
  }, [debouncedQuery, year]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Search Movies</h1>
      <SearchBar
        query={query}
        onQueryChange={setQuery}
        year={year}
        onYearChange={setYear}
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
