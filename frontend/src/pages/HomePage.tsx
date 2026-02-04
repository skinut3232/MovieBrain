import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getWatchHistory } from '../api/watches';
import { useProfile } from '../context/ProfileContext';
import type { WatchResponse } from '../types';
import WatchCard from '../components/watches/WatchCard';

export default function HomePage() {
  const { activeProfile, profiles, createProfile } = useProfile();
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
              await createProfile(newProfileName.trim());
              setNewProfileName('');
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

      <div className="mt-6">
        <Link
          to="/search"
          className="inline-block px-6 py-3 rounded-lg bg-amber-500 hover:bg-amber-600 text-black font-semibold"
        >
          Search Movies
        </Link>
      </div>

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
