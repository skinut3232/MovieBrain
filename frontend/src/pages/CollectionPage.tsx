import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getCollectionDetail } from '../api/catalog';
import MovieGrid from '../components/common/MovieGrid';
import type { CollectionDetail } from '../types';

export default function CollectionPage() {
  const { collectionId } = useParams<{ collectionId: string }>();
  const [collection, setCollection] = useState<CollectionDetail | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadCollection = useCallback(async () => {
    if (!collectionId) return;
    setLoading(true);
    try {
      const data = await getCollectionDetail(Number(collectionId), page, 24);
      setCollection(data);
    } catch {
      setError('Collection not found');
    } finally {
      setLoading(false);
    }
  }, [collectionId, page]);

  useEffect(() => {
    loadCollection();
  }, [loadCollection]);

  if (loading && !collection) return <p className="text-gray-400">Loading...</p>;
  if (error) return <p className="text-red-400">{error}</p>;
  if (!collection) return null;

  const totalPages = Math.ceil(collection.total / 24);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">{collection.name}</h1>
        {collection.description && (
          <p className="text-gray-400">{collection.description}</p>
        )}
        <p className="text-sm text-gray-500 mt-2">
          {collection.total.toLocaleString()} movies
        </p>
      </div>

      {/* Movie Grid */}
      {loading ? (
        <p className="text-gray-400 text-center py-8">Loading...</p>
      ) : (
        <>
          <MovieGrid
            movies={collection.results.map((m) => ({
              id: m.title_id,
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
