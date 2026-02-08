import { useState, type FormEvent } from 'react';
import { logWatch } from '../../api/watches';
import type { WatchCreate } from '../../types';

interface Props {
  titleId: number;
  titleName: string;
  profileId: number;
  onClose: () => void;
  onSaved: () => void;
}

export default function LogWatchModal({
  titleId,
  titleName,
  profileId,
  onClose,
  onSaved,
}: Props) {
  const [rating, setRating] = useState<number | ''>('');
  const [notes, setNotes] = useState('');
  const [watchedDate, setWatchedDate] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const body: WatchCreate = {
      title_id: titleId,
      rating_1_10: rating || null,
      notes: notes || null,
      watched_date: watchedDate || null,
      tag_names: tagInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
    };
    try {
      await logWatch(profileId, body);
      onSaved();
      onClose();
    } catch {
      setError('Failed to save watch. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold text-white mb-4">
          Log Watch: {titleName}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Rating (1-10)
            </label>
            <input
              type="number"
              min={1}
              max={10}
              value={rating}
              onChange={(e) =>
                setRating(e.target.value ? Number(e.target.value) : '')
              }
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Date Watched
            </label>
            <input
              type="date"
              value={watchedDate}
              onChange={(e) => setWatchedDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              placeholder="thriller, favorite, rewatchable"
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              maxLength={4096}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-amber-400"
            />
          </div>
          {error && (
            <p className="text-sm text-red-400">{error}</p>
          )}
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-gray-700 text-gray-300 hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
