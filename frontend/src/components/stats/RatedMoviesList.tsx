import { Link } from 'react-router-dom';
import type { RatedMovie } from '../../types';
import MoviePoster from '../common/MoviePoster';

interface Props {
  title: string;
  data: RatedMovie[];
}

export default function RatedMoviesList({ title, data }: Props) {
  if (data.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-3">
        {data.map((movie, i) => (
          <Link
            key={movie.title_id}
            to={`/movie/${movie.title_id}`}
            className="flex items-center gap-3 hover:bg-gray-700/50 rounded-lg p-1 -m-1 transition-colors"
          >
            <span className="text-gray-500 w-5 text-right text-sm font-mono">
              {i + 1}
            </span>
            <MoviePoster
              posterUrl={movie.poster_url}
              title={movie.primary_title}
              size="sm"
            />
            <div className="min-w-0 flex-1">
              <p className="text-white font-medium truncate">
                {movie.primary_title}
              </p>
              <p className="text-gray-400 text-sm">
                {movie.start_year ?? 'Unknown year'}
              </p>
            </div>
            <span className="text-amber-400 font-bold text-lg whitespace-nowrap">
              {movie.rating}/10
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
