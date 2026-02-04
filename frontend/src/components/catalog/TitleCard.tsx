import { Link } from 'react-router-dom';
import type { TitleSearchResult } from '../../types';

interface Props {
  title: TitleSearchResult;
}

export default function TitleCard({ title }: Props) {
  return (
    <Link
      to={`/movie/${title.id}`}
      className="block bg-gray-800 rounded-lg p-4 hover:bg-gray-750 hover:ring-1 hover:ring-amber-400/50 transition-all"
    >
      <h3 className="font-semibold text-white mb-1">{title.primary_title}</h3>
      <div className="flex items-center gap-3 text-sm text-gray-400">
        {title.start_year && <span>{title.start_year}</span>}
        {title.runtime_minutes && <span>{title.runtime_minutes} min</span>}
        {title.genres && (
          <span className="text-gray-500">{title.genres}</span>
        )}
      </div>
      {title.average_rating && (
        <div className="mt-2 text-sm">
          <span className="text-amber-400">{title.average_rating}</span>
          <span className="text-gray-500">
            {' '}
            ({title.num_votes?.toLocaleString()} votes)
          </span>
        </div>
      )}
    </Link>
  );
}
