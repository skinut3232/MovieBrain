import { Link } from 'react-router-dom';
import type { PersonStat } from '../../types';

interface Props {
  title: string;
  data: PersonStat[];
}

export default function TopPeopleList({ title, data }: Props) {
  if (data.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ol className="space-y-2">
        {data.map((person, i) => (
          <li key={person.person_id} className="flex items-center gap-3">
            <span className="text-gray-500 w-5 text-right text-sm font-mono">
              {i + 1}
            </span>
            <Link
              to={`/person/${person.person_id}`}
              className="text-amber-400 hover:text-amber-300 font-medium truncate"
            >
              {person.name}
            </Link>
            <span className="text-gray-400 text-sm ml-auto whitespace-nowrap">
              {person.count} {person.count === 1 ? 'film' : 'films'}
              {person.avg_rating !== null && (
                <> &middot; {person.avg_rating.toFixed(1)} avg</>
              )}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
