import { useState } from 'react';
import type { OnboardingMovie } from '../../types';
import MoviePoster from '../common/MoviePoster';

interface Props {
  movie: OnboardingMovie;
  onRate: (titleId: number, rating: number) => Promise<void>;
  onSkip: (titleId: number) => void;
}

export default function OnboardingCard({ movie, onRate, onSkip }: Props) {
  const [selectedRating, setSelectedRating] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  const handleRate = async (rating: number) => {
    setSaving(true);
    setSelectedRating(rating);
    try {
      await onRate(movie.title_id, rating);
    } catch {
      setSelectedRating(null);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 flex flex-col items-center text-center">
      <MoviePoster posterUrl={movie.poster_url} title={movie.primary_title} size="lg" />

      <h3 className="text-white font-semibold mt-3 leading-tight">
        {movie.primary_title}
      </h3>
      <div className="text-sm text-gray-400 mt-1">
        {movie.start_year && <span>{movie.start_year}</span>}
      </div>
      {movie.average_rating != null && (
        <div className="text-xs text-gray-500 mt-1">
          IMDb {movie.average_rating.toFixed(1)}
        </div>
      )}

      {/* Rating buttons */}
      {selectedRating ? (
        <div className="mt-3 flex items-center gap-2">
          <span className="text-amber-400 font-semibold">{selectedRating}/10</span>
          <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      ) : (
        <>
          <div className="mt-3 flex flex-wrap justify-center gap-1">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
              <button
                key={n}
                onClick={() => handleRate(n)}
                disabled={saving}
                className="w-8 h-8 rounded text-sm font-medium bg-gray-700 text-gray-300 hover:bg-amber-500 hover:text-black transition-colors disabled:opacity-50"
              >
                {n}
              </button>
            ))}
          </div>
          <button
            onClick={() => onSkip(movie.title_id)}
            className="mt-2 text-xs text-gray-500 hover:text-gray-300"
          >
            Haven't seen it
          </button>
        </>
      )}
    </div>
  );
}
