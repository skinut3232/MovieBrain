import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { completeOnboarding, getOnboardingMovies } from '../api/onboarding';
import { logWatch } from '../api/watches';
import OnboardingCard from '../components/onboarding/OnboardingCard';
import { useProfile } from '../context/ProfileContext';
import type { OnboardingMovie } from '../types';

export default function OnboardingPage() {
  const { activeProfile, refreshProfiles } = useProfile();
  const navigate = useNavigate();
  const [movies, setMovies] = useState<OnboardingMovie[]>([]);
  const [remaining, setRemaining] = useState(0);
  const [ratedCount, setRatedCount] = useState(0);
  const [skippedIds, setSkippedIds] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);

  const profileId = activeProfile?.id;

  const loadMovies = useCallback(async () => {
    if (!profileId) return;
    setLoading(true);
    try {
      const data = await getOnboardingMovies(profileId, 10);
      setMovies(data.movies);
      setRemaining(data.remaining);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [profileId]);

  useEffect(() => {
    loadMovies();
  }, [loadMovies]);

  const handleRate = async (titleId: number, rating: number) => {
    if (!profileId) return;
    await logWatch(profileId, {
      title_id: titleId,
      rating_1_10: rating,
    });
    setRatedCount((prev) => prev + 1);
  };

  const handleSkip = (titleId: number) => {
    setSkippedIds((prev) => new Set(prev).add(titleId));
  };

  const handleLoadMore = async () => {
    if (!profileId) return;
    setSkippedIds(new Set());
    await loadMovies();
  };

  const handleDone = async () => {
    if (!profileId) return;
    await completeOnboarding(profileId);
    await refreshProfiles();
    navigate('/recommend');
  };

  const visibleMovies = movies.filter(
    (m) => !skippedIds.has(m.title_id)
  );

  const MIN_RATINGS = 5;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">
          Rate movies you've seen
        </h1>
        <p className="text-gray-400">
          You've rated <span className="text-amber-400 font-semibold">{ratedCount}</span> movies.
          {ratedCount < MIN_RATINGS ? (
            <> Rate at least <span className="text-amber-400 font-semibold">{MIN_RATINGS}</span> for personalized recommendations.</>
          ) : (
            <> Great! You can keep rating or click Done to continue.</>
          )}
        </p>
        {/* Progress bar */}
        <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-amber-500 transition-all duration-300"
            style={{ width: `${Math.min((ratedCount / MIN_RATINGS) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Movie grid */}
      {loading ? (
        <p className="text-gray-400 text-center py-8">Loading movies...</p>
      ) : visibleMovies.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400 mb-4">
            {remaining > 0
              ? 'All movies in this batch skipped.'
              : 'No more onboarding movies available.'}
          </p>
          {remaining > 0 && (
            <button
              onClick={handleLoadMore}
              className="px-4 py-2 rounded bg-gray-700 text-white hover:bg-gray-600"
            >
              Load More
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {visibleMovies.map((movie) => (
            <OnboardingCard
              key={movie.title_id}
              movie={movie}
              onRate={handleRate}
              onSkip={handleSkip}
            />
          ))}
        </div>
      )}

      {/* Action buttons */}
      <div className="mt-8 flex items-center justify-between">
        {remaining > 0 && visibleMovies.length > 0 && (
          <button
            onClick={handleLoadMore}
            className="px-4 py-2 rounded border border-gray-600 text-gray-300 hover:text-white hover:border-gray-400"
          >
            Load More Movies
          </button>
        )}
        <div className="flex gap-3 ml-auto">
          <button
            onClick={handleDone}
            className="px-6 py-2 rounded text-gray-400 hover:text-white"
          >
            Skip Onboarding
          </button>
          <button
            onClick={handleDone}
            className="px-6 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
