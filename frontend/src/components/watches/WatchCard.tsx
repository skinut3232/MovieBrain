import { Link } from 'react-router-dom';
import type { WatchResponse } from '../../types';

interface Props {
  watch: WatchResponse;
  onDelete: (titleId: number) => void;
}

export default function WatchCard({ watch, onDelete }: Props) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 flex items-start justify-between">
      <div className="flex-1">
        <Link
          to={`/movie/${watch.title_id}`}
          className="font-semibold text-white hover:text-amber-400"
        >
          {watch.title.primary_title}
        </Link>
        <div className="flex flex-wrap items-center gap-3 mt-1 text-sm text-gray-400">
          {watch.title.start_year && <span>{watch.title.start_year}</span>}
          {watch.rating_1_10 && (
            <span className="text-amber-400">
              {watch.rating_1_10}/10
            </span>
          )}
          {watch.watched_date && <span>{watch.watched_date}</span>}
        </div>
        {watch.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {watch.tags.map((tag) => (
              <span
                key={tag.id}
                className="bg-gray-700 text-gray-300 text-xs px-2 py-0.5 rounded"
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
        {watch.notes && (
          <p className="mt-2 text-sm text-gray-400 line-clamp-2">
            {watch.notes}
          </p>
        )}
      </div>
      <button
        onClick={() => onDelete(watch.title_id)}
        className="text-gray-500 hover:text-red-400 ml-4 text-sm"
      >
        Delete
      </button>
    </div>
  );
}
