import { Link } from 'react-router-dom';
import type { ListItemResponse } from '../../types';

interface Props {
  item: ListItemResponse;
  onRemove: (titleId: number) => void;
}

export default function ListItem({ item, onRemove }: Props) {
  return (
    <div className="bg-gray-800 rounded-lg px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-gray-500 text-sm w-6 text-right">
          {item.position}.
        </span>
        <div>
          <Link
            to={`/movie/${item.title_id}`}
            className="font-medium text-white hover:text-amber-400"
          >
            {item.title.primary_title}
          </Link>
          <div className="text-xs text-gray-500">
            {item.title.start_year}
            {item.priority && (
              <span className="ml-2 text-amber-400">
                Priority: {item.priority}
              </span>
            )}
          </div>
        </div>
      </div>
      <button
        onClick={() => onRemove(item.title_id)}
        className="text-gray-500 hover:text-red-400 text-sm"
      >
        Remove
      </button>
    </div>
  );
}
