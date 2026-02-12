import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useProfile } from '../context/ProfileContext';
import { getProfileStats, getWatchHistory } from '../api/watches';
import type { ProfileStats, WatchResponse } from '../types';
import HeroStats from '../components/stats/HeroStats';
import RatingDistributionChart from '../components/stats/RatingDistributionChart';
import GenreBreakdownChart from '../components/stats/GenreBreakdownChart';
import DecadeDistributionChart from '../components/stats/DecadeDistributionChart';
import LanguageDiversityChart from '../components/stats/LanguageDiversityChart';
import TopPeopleList from '../components/stats/TopPeopleList';
import CriticComparisonChart from '../components/stats/CriticComparisonChart';
import MoviesPerMonthChart from '../components/stats/MoviesPerMonthChart';
import RatingTrendChart from '../components/stats/RatingTrendChart';
import RatedMoviesList from '../components/stats/RatedMoviesList';
import RecentWatches from '../components/stats/RecentWatches';
import WatchHistory from '../components/watches/WatchHistory';

export default function WatchHistoryPage() {
  const { activeProfile } = useProfile();
  const [stats, setStats] = useState<ProfileStats | null>(null);
  const [recentWatches, setRecentWatches] = useState<WatchResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    if (!activeProfile) return;
    setLoading(true);
    setError(null);
    Promise.all([
      getProfileStats(activeProfile.id),
      getWatchHistory(activeProfile.id, { limit: 10, sort_by: 'watched_date' }),
    ])
      .then(([statsData, historyData]) => {
        setStats(statsData);
        setRecentWatches(historyData.results);
      })
      .catch(() => {
        setError('Failed to load stats. Please try again.');
      })
      .finally(() => setLoading(false));
  }, [activeProfile, retryCount]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Your Movie Stats</h1>
        <div className="text-gray-400">Loading stats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Your Movie Stats</h1>
        <div className="bg-red-900/30 border border-red-700 rounded-xl p-6 text-center space-y-3">
          <p className="text-red-300">{error}</p>
          <button
            onClick={() => setRetryCount((c) => c + 1)}
            className="bg-amber-500 text-black font-semibold px-6 py-2 rounded-lg hover:bg-amber-400 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!stats || stats.total_movies === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Your Movie Stats</h1>
        <div className="bg-gray-800 rounded-xl p-8 text-center">
          <p className="text-gray-400 text-lg mb-4">
            No movies watched yet. Start tracking your watches to see your stats!
          </p>
          <Link
            to="/search"
            className="inline-block bg-amber-500 text-black font-semibold px-6 py-2 rounded-lg hover:bg-amber-400 transition-colors"
          >
            Search Movies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-3xl font-bold">Your Movie Stats</h1>

      <HeroStats
        totalMovies={stats.total_movies}
        avgRating={stats.avg_rating}
        totalRuntimeMinutes={stats.total_runtime_minutes}
        totalRewatches={stats.total_rewatches}
        uniqueLanguages={stats.unique_languages}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RatingDistributionChart data={stats.rating_distribution} />
        <GenreBreakdownChart data={stats.genre_breakdown} />
        <DecadeDistributionChart data={stats.decade_distribution} />
        <LanguageDiversityChart data={stats.language_diversity} />
        <TopPeopleList title="Top Directors" data={stats.top_directors} />
        <TopPeopleList title="Top Actors" data={stats.top_actors} />

        <div className="lg:col-span-2">
          <CriticComparisonChart
            data={stats.critic_comparisons}
            avgUserScore={stats.avg_user_score}
            avgCriticScore={stats.avg_critic_score}
            avgDifference={stats.avg_difference}
          />
        </div>

        <div className="lg:col-span-2">
          <MoviesPerMonthChart data={stats.movies_per_month} />
        </div>

        <div className="lg:col-span-2">
          <RatingTrendChart data={stats.rating_over_time} />
        </div>

        <RatedMoviesList title="Highest Rated" data={stats.highest_rated} />
        <RatedMoviesList title="Lowest Rated" data={stats.lowest_rated} />
      </div>

      <RecentWatches watches={recentWatches} />

      <div className="border-t border-gray-700 pt-6">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="text-amber-400 hover:text-amber-300 font-medium text-lg"
        >
          {showHistory ? 'Hide Full History' : 'View Full History'}
        </button>
        {showHistory && (
          <div className="mt-4">
            <WatchHistory />
          </div>
        )}
      </div>
    </div>
  );
}
