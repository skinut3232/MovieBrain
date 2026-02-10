import { Link } from 'react-router-dom';
import type { RecommendedTitle } from '../../types';
import MoviePoster from '../common/MoviePoster';

interface RecommendCardProps {
  movie: RecommendedTitle;
}

export default function RecommendCard({ movie }: RecommendCardProps) {
  return (
    <Link
      to={`/movie/${movie.title_id}`}
      className="block bg-gray-900 border border-gray-700 rounded-lg p-4 hover:border-amber-500 transition-colors"
    >
      <div className="flex items-start gap-4">
        <MoviePoster posterUrl={movie.poster_url} title={movie.primary_title} size="sm" />
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate">
            {movie.primary_title}
          </h3>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
            {movie.start_year && <span>{movie.start_year}</span>}
            {movie.runtime_minutes && <span>{movie.runtime_minutes} min</span>}
            {movie.genres && <span>{movie.genres}</span>}
          </div>
          {movie.rt_critic_score != null && (
            <div className="mt-2 text-sm">
              <span className={movie.rt_critic_score >= 60 ? 'text-red-400' : 'text-yellow-500'}>
                {movie.rt_critic_score >= 60 ? '🍅' : '🤢'} {movie.rt_critic_score}%
              </span>
            </div>
          )}
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
