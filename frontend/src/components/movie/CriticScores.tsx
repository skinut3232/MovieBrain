interface Props {
  imdbRating: number | null;
  imdbVotes: number | null;
  rtCriticScore: number | null;
  rtAudienceScore: number | null;
  metacriticScore: number | null;
  imdbTconst: string;
}

function MetacriticBadge({ score }: { score: number }) {
  const bg =
    score >= 61
      ? 'bg-green-600'
      : score >= 40
        ? 'bg-yellow-500'
        : 'bg-red-600';

  return (
    <span
      className={`${bg} text-white font-bold text-sm px-1.5 py-0.5 rounded`}
    >
      {score}
    </span>
  );
}

export default function CriticScores({
  imdbRating,
  imdbVotes,
  rtCriticScore,
  rtAudienceScore,
  metacriticScore,
  imdbTconst,
}: Props) {
  const hasAnyScore =
    imdbRating != null || rtCriticScore != null || metacriticScore != null;

  if (!hasAnyScore) return null;

  return (
    <div className="flex flex-wrap items-center gap-5 text-sm">
      {/* IMDb */}
      {imdbRating != null && (
        <a
          href={`https://www.imdb.com/title/${imdbTconst}/`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 hover:opacity-80 transition"
          title="IMDb rating"
        >
          <span className="text-amber-400 text-base">&#9733;</span>
          <span className="text-white font-semibold">{imdbRating}</span>
          <span className="text-gray-400">/10</span>
          {imdbVotes != null && (
            <span className="text-gray-500 text-xs ml-0.5">
              ({imdbVotes.toLocaleString()})
            </span>
          )}
        </a>
      )}

      {/* Rotten Tomatoes Tomatometer */}
      {rtCriticScore != null && (
        <div className="flex items-center gap-1.5" title="Rotten Tomatoes Tomatometer">
          <span className="text-base">{rtCriticScore >= 60 ? '\uD83C\uDF45' : '\uD83E\uDD22'}</span>
          <span className="text-white font-semibold">{rtCriticScore}%</span>
          <span className="text-gray-500 text-xs">Tomatometer</span>
        </div>
      )}

      {/* RT Audience Score (future) */}
      {rtAudienceScore != null && (
        <div className="flex items-center gap-1.5" title="RT Audience Score">
          <span className="text-base">&#127871;</span>
          <span className="text-white font-semibold">{rtAudienceScore}%</span>
          <span className="text-gray-500 text-xs">Audience</span>
        </div>
      )}

      {/* Metacritic */}
      {metacriticScore != null && (
        <div className="flex items-center gap-1.5" title="Metacritic Metascore">
          <MetacriticBadge score={metacriticScore} />
          <span className="text-gray-500 text-xs">Metascore</span>
        </div>
      )}
    </div>
  );
}
