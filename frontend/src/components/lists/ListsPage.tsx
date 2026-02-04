import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { createList, getLists } from '../../api/lists';
import { useProfile } from '../../context/ProfileContext';
import type { ListResponse, ListType } from '../../types';

export default function ListsPage() {
  const { activeProfile } = useProfile();
  const [lists, setLists] = useState<ListResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newType, setNewType] = useState<ListType>('custom');

  const profileId = activeProfile?.id;

  const loadLists = useCallback(async () => {
    if (!profileId) return;
    setLoading(true);
    try {
      const data = await getLists(profileId);
      setLists(data);
    } finally {
      setLoading(false);
    }
  }, [profileId]);

  useEffect(() => {
    loadLists();
  }, [loadLists]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!profileId || !newName.trim()) return;
    await createList(profileId, newName.trim(), newType);
    setNewName('');
    setShowCreate(false);
    loadLists();
  };

  if (!profileId) {
    return <p className="text-gray-400">Please select a profile.</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-white">My Lists</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold text-sm"
        >
          New List
        </button>
      </div>

      {showCreate && (
        <form
          onSubmit={handleCreate}
          className="bg-gray-800 rounded-lg p-4 mb-4 flex flex-wrap gap-3 items-end"
        >
          <div className="flex-1 min-w-48">
            <label className="block text-sm text-gray-400 mb-1">Name</label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              required
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-white focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Type</label>
            <select
              value={newType}
              onChange={(e) => setNewType(e.target.value as ListType)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-white"
            >
              <option value="custom">Custom</option>
              <option value="watchlist">Watchlist</option>
              <option value="favorites">Favorites</option>
              <option value="rewatch">Rewatch</option>
            </select>
          </div>
          <button
            type="submit"
            className="px-4 py-1.5 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold"
          >
            Create
          </button>
        </form>
      )}

      {loading && <p className="text-gray-400">Loading...</p>}

      {!loading && lists.length === 0 && (
        <p className="text-gray-500">
          No lists yet. Create one to get started.
        </p>
      )}

      <div className="grid gap-3">
        {lists.map((list) => (
          <Link
            key={list.id}
            to={`/lists/${list.id}`}
            className="block bg-gray-800 rounded-lg p-4 hover:ring-1 hover:ring-amber-400/50 transition-all"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-white">{list.name}</h3>
                <p className="text-sm text-gray-400">
                  {list.list_type} &middot; {list.item_count} item
                  {list.item_count !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
