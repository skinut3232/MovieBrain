import { Link } from 'react-router-dom';
import MoviePoster from './MoviePoster';

interface MovieItem {
  id: number;
  primary_title: string;
  start_year: number | null;
  genres?: string | null;
  average_rating?: number | null;
  num_votes?: number | null;
  poster_url: string | null;
}

interface Props {
  movies: MovieItem[];
}

export default function MovieGrid({ movies }: Props) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {movies.map((movie) => (
        <Link
          key={movie.id}
          to={`/movie/${movie.id}`}
          className="group"
        >
          <div className="relative">
            <MoviePoster
              posterUrl={movie.poster_url}
              title={movie.primary_title}
              size="md"
            />
            {movie.average_rating && (
              <div className="absolute top-2 right-2 bg-black/80 text-amber-400 text-xs font-semibold px-1.5 py-0.5 rounded">
                {movie.average_rating.toFixed(1)}
              </div>
            )}
          </div>
          <div className="mt-2">
            <h3 className="text-sm font-medium text-gray-200 group-hover:text-white truncate">
              {movie.primary_title}
            </h3>
            <p className="text-xs text-gray-500">
              {movie.start_year || 'Unknown year'}
            </p>
          </div>
        </Link>
      ))}
    </div>
  );
}
