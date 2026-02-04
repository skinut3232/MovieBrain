import type { TitleDetailResponse } from '../../types';
import MovieActions from './MovieActions';

interface Props {
  title: TitleDetailResponse;
}

export default function MovieDetail({ title }: Props) {
  const directors = title.principals.filter(
    (p) => p.category === 'director'
  );
  const cast = title.principals.filter(
    (p) => p.category === 'actor' || p.category === 'actress'
  );

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-1">
        {title.primary_title}
      </h1>
      {title.original_title && title.original_title !== title.primary_title && (
        <p className="text-gray-400 text-sm mb-2">
          Original: {title.original_title}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-4">
        {title.start_year && <span>{title.start_year}</span>}
        {title.runtime_minutes && <span>{title.runtime_minutes} min</span>}
        {title.genres && (
          <span className="text-gray-500">{title.genres}</span>
        )}
        {title.rating && (
          <span>
            <span className="text-amber-400 font-semibold">
              {title.rating.average_rating}
            </span>{' '}
            ({title.rating.num_votes?.toLocaleString()} votes)
          </span>
        )}
      </div>

      <MovieActions titleId={title.id} titleName={title.primary_title} />

      {directors.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-2">
            Director{directors.length > 1 ? 's' : ''}
          </h2>
          <div className="flex flex-wrap gap-2">
            {directors.map((d, i) => (
              <span
                key={i}
                className="bg-gray-800 px-3 py-1 rounded text-sm text-gray-300"
              >
                {d.person.primary_name}
              </span>
            ))}
          </div>
        </div>
      )}

      {cast.length > 0 && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold text-gray-200 mb-2">Cast</h2>
          <div className="grid gap-2">
            {cast.map((p, i) => (
              <div key={i} className="text-sm text-gray-300">
                <span className="font-medium">{p.person.primary_name}</span>
                {p.characters && (
                  <span className="text-gray-500 ml-2">
                    as {p.characters.replace(/[\[\]"]/g, '')}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
