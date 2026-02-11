import { Link } from 'react-router-dom';
import type { WatchResponse } from '../../types';
import MoviePoster from '../common/MoviePoster';

interface Props {
  watches: WatchResponse[];
}

export default function RecentWatches({ watches }: Props) {
  if (watches.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Recent Watches</h3>
      <div className="flex gap-4 overflow-x-auto pb-2">
        {watches.map((w) => (
          <Link
            key={w.id}
            to={`/movie/${w.title_id}`}
            className="flex-shrink-0 w-28 group"
          >
            <MoviePoster
              posterUrl={w.title.poster_url}
              title={w.title.primary_title}
              size="md"
            />
            <p className="text-sm text-gray-300 mt-1 truncate group-hover:text-amber-400 transition-colors">
              {w.title.primary_title}
            </p>
            {w.rating_1_10 !== null && (
              <p className="text-xs text-amber-400">{w.rating_1_10}/10</p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
