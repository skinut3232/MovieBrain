import { useState } from 'react';
import { Link } from 'react-router-dom';
import { getRandomMovie } from '../../api/catalog';
import type { RandomMovie } from '../../types';

interface Props {
  genres: string[];
  excludeWatchedProfileId?: number;
}

export default function SurpriseMe({ genres, excludeWatchedProfileId }: Props) {
  const [selectedGenre, setSelectedGenre] = useState('');
  const [movie, setMovie] = useState<RandomMovie | null>(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState('');

  const handlePickRandom = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await getRandomMovie({
        genre: selectedGenre || undefined,
        excludeWatchedProfileId,
      });
      setMovie(result);
      setShowModal(true);
    } catch (err) {
      setError('No movies found. Try a different genre.');
    } finally {
      setLoading(false);
    }
  };

  const handleTryAnother = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await getRandomMovie({
        genre: selectedGenre || undefined,
        excludeWatchedProfileId,
      });
      setMovie(result);
    } catch (err) {
      setError('No more movies found. Try a different genre.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="bg-gradient-to-r from-amber-500/20 to-amber-600/10 border border-amber-500/30 rounded-xl p-6 mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <h2 className="text-xl font-bold text-white mb-1">Surprise Me</h2>
            <p className="text-gray-400 text-sm">
              Can't decide what to watch? Let us pick a random movie for you!
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-300 text-sm focus:outline-none focus:border-amber-500"
            >
              <option value="">Any Genre</option>
              {genres.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
            <button
              onClick={handlePickRandom}
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-black font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {loading ? 'Picking...' : 'Pick a Random Movie'}
            </button>
          </div>
        </div>
        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
      </div>

      {/* Modal */}
      {showModal && movie && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setShowModal(false)}
        >
          <div
            className="bg-gray-900 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex flex-col md:flex-row gap-6 p-6">
              {/* Poster */}
              <div className="flex-shrink-0 mx-auto md:mx-0">
                {movie.poster_url ? (
                  <img
                    src={movie.poster_url}
                    alt={movie.primary_title}
                    className="w-48 h-72 object-cover rounded-lg"
                  />
                ) : (
                  <div className="w-48 h-72 bg-gray-700 rounded-lg flex items-center justify-center">
                    <span className="text-gray-500 text-sm text-center px-4">
                      {movie.primary_title}
                    </span>
                  </div>
                )}
              </div>

              {/* Details */}
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white mb-2">
                  {movie.primary_title}
                </h2>
                <div className="flex flex-wrap items-center gap-3 text-sm text-gray-400 mb-4">
                  {movie.start_year && <span>{movie.start_year}</span>}
                  {movie.runtime_minutes && (
                    <span>{movie.runtime_minutes} min</span>
                  )}
                  {movie.average_rating != null && (
                    <span className="flex items-center gap-1 text-amber-400 font-semibold">
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      {movie.average_rating.toFixed(1)}
                    </span>
                  )}
                </div>
                {movie.genres && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {movie.genres.split(',').map((g) => (
                      <span
                        key={g.trim()}
                        className="px-2 py-1 bg-gray-800 text-gray-300 text-xs rounded"
                      >
                        {g.trim()}
                      </span>
                    ))}
                  </div>
                )}
                {movie.overview && (
                  <p className="text-gray-300 text-sm leading-relaxed mb-6">
                    {movie.overview}
                  </p>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={handleTryAnother}
                    disabled={loading}
                    className="px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 transition disabled:opacity-50"
                  >
                    {loading ? 'Loading...' : 'Try Another'}
                  </button>
                  <Link
                    to={`/movie/${movie.id}`}
                    className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-black font-semibold transition"
                    onClick={() => setShowModal(false)}
                  >
                    View Details
                  </Link>
                </div>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
              aria-label="Close"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}
