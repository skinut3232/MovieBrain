import { useCallback, useEffect, useState } from 'react';
import { deleteWatch, getWatchHistory } from '../../api/watches';
import { useProfile } from '../../context/ProfileContext';
import type { PaginatedWatchHistory as WatchHistoryData } from '../../types';
import WatchCard from './WatchCard';

export default function WatchHistory() {
  const { activeProfile } = useProfile();
  const [data, setData] = useState<WatchHistoryData | null>(null);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('watched_date');
  const [tagFilter, setTagFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const profileId = activeProfile?.id;

  const loadHistory = useCallback(async () => {
    if (!profileId) return;
    setLoading(true);
    try {
      const result = await getWatchHistory(profileId, {
        page,
        sort_by: sortBy,
        tag: tagFilter || undefined,
      });
      setData(result);
    } finally {
      setLoading(false);
    }
  }, [profileId, page, sortBy, tagFilter]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDelete = async (titleId: number) => {
    if (!profileId || !confirm('Remove this watch?')) return;
    await deleteWatch(profileId, titleId);
    loadHistory();
  };

  if (!profileId) {
    return (
      <p className="text-gray-400">Please select a profile to view history.</p>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Watch History</h1>

      <div className="flex flex-wrap gap-3 mb-4">
        <select
          value={sortBy}
          onChange={(e) => {
            setSortBy(e.target.value);
            setPage(1);
          }}
          className="bg-gray-800 border border-gray-600 rounded px-3 py-1.5 text-sm text-white"
        >
          <option value="watched_date">Sort by Date</option>
          <option value="rating">Sort by Rating</option>
          <option value="created_at">Sort by Added</option>
        </select>
        <input
          type="text"
          placeholder="Filter by tag..."
          value={tagFilter}
          onChange={(e) => {
            setTagFilter(e.target.value);
            setPage(1);
          }}
          className="bg-gray-800 border border-gray-600 rounded px-3 py-1.5 text-sm text-white placeholder-gray-500"
        />
      </div>

      {loading && <p className="text-gray-400">Loading...</p>}

      {data && (
        <>
          <p className="text-sm text-gray-400 mb-3">
            {data.total} movie{data.total !== 1 ? 's' : ''} logged
          </p>
          <div className="grid gap-3">
            {data.results.map((watch) => (
              <WatchCard
                key={watch.id}
                watch={watch}
                onDelete={handleDelete}
              />
            ))}
          </div>
          {data.total > data.limit && (
            <div className="flex items-center justify-center gap-3 mt-6">
              <button
                onClick={() => setPage((p) => p - 1)}
                disabled={page <= 1}
                className="px-3 py-1 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-30"
              >
                Previous
              </button>
              <span className="text-sm text-gray-400">
                Page {page} of {Math.ceil(data.total / data.limit)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(data.total / data.limit)}
                className="px-3 py-1 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-30"
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
