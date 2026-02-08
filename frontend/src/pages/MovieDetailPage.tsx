import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getTitleDetail } from '../api/catalog';
import MovieDetail from '../components/movie/MovieDetail';
import type { TitleDetailResponse } from '../types';

export default function MovieDetailPage() {
  const { titleId } = useParams<{ titleId: string }>();
  const [title, setTitle] = useState<TitleDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!titleId) return;
    let cancelled = false;
    setLoading(true);
    getTitleDetail(Number(titleId))
      .then((data) => { if (!cancelled) setTitle(data); })
      .catch(() => { if (!cancelled) setError('Movie not found'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [titleId]);

  if (loading) return <p className="text-gray-400">Loading...</p>;
  if (error) return <p className="text-red-400">{error}</p>;
  if (!title) return null;

  return <MovieDetail title={title} />;
}
