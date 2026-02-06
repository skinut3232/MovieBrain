import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getWatchHistory } from '../api/watches';
import { useProfile } from '../context/ProfileContext';
import type { WatchResponse } from '../types';
import WatchCard from '../components/watches/WatchCard';

export default function HomePage() {
  const { activeProfile, profiles, createProfile } = useProfile();
  const navigate = useNavigate();
  const [recentWatches, setRecentWatches] = useState<WatchResponse[]>([]);
  const [newProfileName, setNewProfileName] = useState('');

  useEffect(() => {
    if (!activeProfile) return;
    getWatchHistory(activeProfile.id, { limit: 5, sort_by: 'created_at' }).then(
      (data) => setRecentWatches(data.results)
    );
  }, [activeProfile]);

  if (profiles.length === 0) {
    return (
      <div className="max-w-md mx-auto mt-12">
        <h1 className="text-2xl font-bold text-white mb-4">Welcome to MovieBrain</h1>
        <p className="text-gray-400 mb-4">
          Create a profile to start tracking movies.
        </p>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            if (newProfileName.trim()) {
              const profile = await createProfile(newProfileName.trim());
              setNewProfileName('');
              // Redirect new profiles to onboarding
              if (profile && !profile.onboarding_completed) {
                navigate('/onboard');
              }
            }
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={newProfileName}
            onChange={(e) => setNewProfileName(e.target.value)}
            placeholder="Profile name"
            required
            className="flex-1 bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold"
          >
            Create
          </button>
        </form>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-2">
        Welcome, {activeProfile?.name}
      </h1>

      <div className="mt-6 flex gap-3">
        <Link
          to="/search"
          className="inline-block px-6 py-3 rounded-lg bg-amber-500 hover:bg-amber-600 text-black font-semibold"
        >
          Search Movies
        </Link>
        <Link
          to="/recommend"
          className="inline-block px-6 py-3 rounded-lg border border-amber-500 text-amber-400 hover:bg-amber-500/10 font-semibold"
        >
          Get Recommendations
        </Link>
      </div>

      {/* Onboarding prompt for profiles that haven't completed it */}
      {activeProfile && !activeProfile.onboarding_completed && (
        <div className="mt-6 p-4 rounded-lg border border-amber-500/50 bg-amber-500/10">
          <p className="text-amber-300 mb-2">
            Rate some movies to get personalized recommendations!
          </p>
          <Link
            to="/onboard"
            className="inline-block px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold text-sm"
          >
            Start Quick Rating
          </Link>
        </div>
      )}

      {recentWatches.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-200">
              Recent Watches
            </h2>
            <Link
              to="/history"
              className="text-sm text-amber-400 hover:underline"
            >
              View all
            </Link>
          </div>
          <div className="grid gap-3">
            {recentWatches.map((w) => (
              <WatchCard key={w.id} watch={w} onDelete={() => {}} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
