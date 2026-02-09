import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getRecommendations, getTasteProfile, recomputeTaste } from '../api/recommend';
import MoodInput from '../components/recommend/MoodInput';
import RecommendCard from '../components/recommend/RecommendCard';
import RecommendFilters from '../components/recommend/RecommendFilters';
import { useProfile } from '../context/ProfileContext';
import type { RecommendedTitle, RecommendRequest, TasteProfileResponse } from '../types';

export default function RecommendPage() {
  const { activeProfile } = useProfile();
  const [results, setResults] = useState<RecommendedTitle[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [fallbackMode, setFallbackMode] = useState(false);
  const [moodMode, setMoodMode] = useState(false);
  const [mood, setMood] = useState('');
  const [loading, setLoading] = useState(false);
  const [taste, setTaste] = useState<TasteProfileResponse | null>(null);
  const [filters, setFilters] = useState<RecommendRequest>({});
  const [error, setError] = useState<string | null>(null);

  const profileId = activeProfile?.id;

  const loadTaste = useCallback(async () => {
    if (!profileId) return;
    try {
      const data = await getTasteProfile(profileId);
      setTaste(data);
    } catch {
      // Taste endpoint may not be available yet
    }
  }, [profileId]);

  const loadRecommendations = useCallback(async (currentPage: number, currentFilters: RecommendRequest, currentMood?: string) => {
    if (!profileId) return;
    setLoading(true);
    setError(null);
    try {
      const request: RecommendRequest = {
        ...currentFilters,
        limit,
        page: currentPage,
      };
      if (currentMood) request.mood = currentMood;
      const data = await getRecommendations(profileId, request);
      setResults(data.results);
      setTotal(data.total);
      setPage(data.page);
      setFallbackMode(data.fallback_mode);
      setMoodMode(data.mood_mode);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Request failed';
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || msg);
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [profileId, limit]);

  useEffect(() => {
    loadTaste();
    loadRecommendations(1, filters);
  }, [loadTaste, loadRecommendations]); // runs when profileId changes (via memoized deps)

  const handleFiltersApply = (newFilters: RecommendRequest) => {
    setFilters(newFilters);
    setPage(1);
    loadRecommendations(1, newFilters, mood || undefined);
  };

  const handlePageChange = (newPage: number) => {
    loadRecommendations(newPage, filters, mood || undefined);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRecompute = async () => {
    if (!profileId) return;
    try {
      const data = await recomputeTaste(profileId);
      setTaste(data);
      loadRecommendations(1, filters, mood || undefined);
    } catch {
      // ignore
    }
  };

  const handleMoodSearch = (moodText: string) => {
    setMood(moodText);
    setPage(1);
    loadRecommendations(1, filters, moodText);
  };

  const handleMoodClear = () => {
    setMood('');
    setMoodMode(false);
    setPage(1);
    loadRecommendations(1, filters);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Recommendations</h1>

      {/* Onboarding CTA banner when too few ratings */}
      {taste && taste.num_rated_movies < taste.min_required && (
        <div className="mb-4 p-4 rounded-lg border border-amber-500/50 bg-amber-500/10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-300 font-medium">
                Rate at least {taste.min_required} movies for personalized recommendations
              </p>
              <p className="text-amber-300/70 text-sm mt-1">
                You've rated {taste.num_rated_movies} so far. Quick-rate popular movies to get started!
              </p>
            </div>
            <Link
              to="/onboard"
              className="shrink-0 ml-4 px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold text-sm"
            >
              Quick Rate
            </Link>
          </div>
        </div>
      )}

      {/* Taste status banner */}
      {taste && taste.num_rated_movies >= taste.min_required && (
        <div className={`mb-4 p-4 rounded-lg border ${
          taste.has_taste_vector
            ? 'bg-green-900/20 border-green-700 text-green-300'
            : 'bg-yellow-900/20 border-yellow-700 text-yellow-300'
        }`}>
          {taste.has_taste_vector ? (
            <div className="flex items-center justify-between">
              <span>
                Personalized recommendations based on {taste.num_rated_movies} rated movies.
              </span>
              <button
                onClick={handleRecompute}
                className="text-sm underline hover:no-underline"
              >
                Recompute
              </button>
            </div>
          ) : (
            <span>
              Rate at least {taste.min_required} movies to get personalized recommendations.
              You've rated {taste.num_rated_movies} so far.
            </span>
          )}
        </div>
      )}

      {/* Fallback mode indicator */}
      {fallbackMode && !loading && results.length > 0 && (
        <p className="text-sm text-gray-400 mb-3">
          Showing popular movies. Rate more movies for personalized results.
        </p>
      )}

      {/* Mood search */}
      <MoodInput onSearch={handleMoodSearch} onClear={handleMoodClear} loading={loading} />

      {/* Mood mode banner */}
      {moodMode && mood && !loading && (
        <div className="mb-4 p-3 rounded-lg border border-amber-500/30 bg-amber-500/10">
          <p className="text-amber-300 text-sm">
            Showing movies matching: <span className="font-medium">"{mood}"</span>
          </p>
        </div>
      )}

      {/* Filter panel */}
      <RecommendFilters onApply={handleFiltersApply} loading={loading} />

      {/* Error banner */}
      {error && (
        <div className="mb-4 p-3 rounded-lg border border-red-500/50 bg-red-500/10">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      <div className="mt-4">
        {loading ? (
          <p className="text-gray-400 py-8 text-center">Loading recommendations...</p>
        ) : results.length === 0 ? (
          <p className="text-gray-400 py-8 text-center">
            No recommendations found. Try adjusting your filters.
          </p>
        ) : (
          <>
            <p className="text-sm text-gray-400 mb-3">
              {total} results (page {page} of {totalPages})
            </p>
            <div className="grid gap-3">
              {results.map((movie) => (
                <RecommendCard key={movie.title_id} movie={movie} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page <= 1}
                  className="px-3 py-1 rounded border border-gray-600 text-gray-300 hover:text-white hover:border-gray-400 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-gray-400 text-sm">
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page >= totalPages}
                  className="px-3 py-1 rounded border border-gray-600 text-gray-300 hover:text-white hover:border-gray-400 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
