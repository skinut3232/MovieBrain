import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getSimilarMovies } from '../../api/catalog';
import type { SimilarTitle } from '../../types';
import MoviePoster from '../common/MoviePoster';

interface Props {
  titleId: number;
}

export default function SimilarMovies({ titleId }: Props) {
  const [similar, setSimilar] = useState<SimilarTitle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getSimilarMovies(titleId, 6)
      .then(setSimilar)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [titleId]);

  if (loading) {
    return (
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-200 mb-3">Similar Movies</h2>
        <p className="text-gray-400 text-sm">Loading...</p>
      </div>
    );
  }

  if (similar.length === 0) {
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-lg font-semibold text-gray-200 mb-3">Similar Movies</h2>
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
        {similar.map((movie) => (
          <Link
            key={movie.id}
            to={`/movie/${movie.id}`}
            className="group"
          >
            <div className="relative">
              <MoviePoster
                posterUrl={movie.poster_url}
                title={movie.primary_title}
                size="sm"
              />
              {movie.average_rating && (
                <div className="absolute top-1 right-1 bg-black/80 text-amber-400 text-xs font-semibold px-1 py-0.5 rounded">
                  {movie.average_rating.toFixed(1)}
                </div>
              )}
            </div>
            <h3 className="mt-1 text-xs text-gray-300 group-hover:text-white truncate">
              {movie.primary_title}
            </h3>
            <p className="text-xs text-gray-500">{movie.start_year}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
