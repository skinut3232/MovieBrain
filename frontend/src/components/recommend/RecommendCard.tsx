import { Link } from 'react-router-dom';
import type { RecommendedTitle } from '../../types';

interface RecommendCardProps {
  movie: RecommendedTitle;
}

export default function RecommendCard({ movie }: RecommendCardProps) {
  return (
    <Link
      to={`/movie/${movie.title_id}`}
      className="block bg-gray-900 border border-gray-700 rounded-lg p-4 hover:border-amber-500 transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate">
            {movie.primary_title}
          </h3>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
            {movie.start_year && <span>{movie.start_year}</span>}
            {movie.runtime_minutes && <span>{movie.runtime_minutes} min</span>}
            {movie.genres && <span>{movie.genres}</span>}
          </div>
          <div className="flex items-center gap-3 mt-2 text-sm">
            {movie.average_rating != null && (
              <span className="text-amber-400">
                IMDb {movie.average_rating.toFixed(1)}
              </span>
            )}
            {movie.num_votes != null && (
              <span className="text-gray-500">
                {movie.num_votes.toLocaleString()} votes
              </span>
            )}
          </div>
        </div>

        {movie.similarity_score != null && (
          <span className="shrink-0 px-2 py-1 rounded text-xs font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">
            {(movie.similarity_score * 100).toFixed(0)}% match
          </span>
        )}
      </div>
    </Link>
  );
}
