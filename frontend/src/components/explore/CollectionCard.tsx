import { Link } from 'react-router-dom';
import type { CollectionBrief } from '../../types';

interface Props {
  collection: CollectionBrief;
}

export default function CollectionCard({ collection }: Props) {
  return (
    <Link
      to={`/collections/${collection.id}`}
      className="block p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition group"
    >
      <h3 className="font-semibold text-white group-hover:text-amber-400 transition">
        {collection.name}
      </h3>
      {collection.description && (
        <p className="text-sm text-gray-400 mt-1 line-clamp-2">
          {collection.description}
        </p>
      )}
      <span className="inline-block mt-2 text-xs text-gray-500">
        {collection.collection_type}
      </span>
    </Link>
  );
}
