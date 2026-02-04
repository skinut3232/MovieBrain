import type { PaginatedSearchResponse } from '../../types';
import TitleCard from './TitleCard';

interface Props {
  data: PaginatedSearchResponse;
  page: number;
  onPageChange: (p: number) => void;
}

export default function SearchResults({ data, page, onPageChange }: Props) {
  const totalPages = Math.ceil(data.total / data.limit);

  return (
    <div>
      <p className="text-sm text-gray-400 mb-4">
        {data.total} result{data.total !== 1 ? 's' : ''} found
      </p>
      <div className="grid gap-3">
        {data.results.map((title) => (
          <TitleCard key={title.id} title={title} />
        ))}
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 mt-6">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="px-3 py-1 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-gray-400">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="px-3 py-1 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
