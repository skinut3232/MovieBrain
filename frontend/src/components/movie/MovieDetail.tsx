import { Link } from 'react-router-dom';
import type { TitleDetailResponse } from '../../types';
import MoviePoster from '../common/MoviePoster';
import CriticScores from './CriticScores';
import MovieActions from './MovieActions';
import SimilarMovies from './SimilarMovies';
import TrailerEmbed from './TrailerEmbed';
import WatchProviders from './WatchProviders';

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
      <div className="flex gap-6 mb-4">
        <MoviePoster posterUrl={title.poster_url} title={title.primary_title} size="lg" />
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-white mb-1">
            {title.primary_title}
          </h1>
          {title.original_title && title.original_title !== title.primary_title && (
            <p className="text-gray-400 text-sm mb-2">
              Original: {title.original_title}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-3">
            {title.start_year && <span>{title.start_year}</span>}
            {title.runtime_minutes && <span>{title.runtime_minutes} min</span>}
            {title.genres && (
              <span className="text-gray-500">{title.genres}</span>
            )}
          </div>

          <div className="mb-4">
            <CriticScores
              imdbRating={title.rating?.average_rating ?? null}
              imdbVotes={title.rating?.num_votes ?? null}
              rtCriticScore={title.rt_critic_score}
              rtAudienceScore={title.rt_audience_score}
              metacriticScore={title.metacritic_score}
              imdbTconst={title.imdb_tconst}
            />
          </div>

          <MovieActions titleId={title.id} titleName={title.primary_title} />
        </div>
      </div>

      {/* Plot Summary */}
      {title.overview && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-2">Plot</h2>
          <p className="text-gray-300 leading-relaxed">{title.overview}</p>
        </div>
      )}

      {/* Where to Watch */}
      <WatchProviders titleId={title.id} />

      {/* Directors */}
      {directors.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-2">
            Director{directors.length > 1 ? 's' : ''}
          </h2>
          <div className="flex flex-wrap gap-2">
            {directors.map((d, i) => (
              <Link
                key={i}
                to={`/person/${d.person.id}`}
                className="bg-gray-800 px-3 py-1 rounded text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition"
              >
                {d.person.primary_name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Cast */}
      {cast.length > 0 && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold text-gray-200 mb-2">Cast</h2>
          <div className="grid gap-2">
            {cast.map((p, i) => (
              <div key={i} className="text-sm text-gray-300">
                <Link
                  to={`/person/${p.person.id}`}
                  className="font-medium hover:text-amber-400 transition"
                >
                  {p.person.primary_name}
                </Link>
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

      {/* Trailer */}
      {title.trailer_key && (
        <TrailerEmbed trailerKey={title.trailer_key} title={title.primary_title} />
      )}

      {/* Similar Movies */}
      <SimilarMovies titleId={title.id} />
    </div>
  );
}
