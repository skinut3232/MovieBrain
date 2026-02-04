import { useEffect, useState } from 'react';
import { createFlag, deleteFlag, getFlags } from '../../api/flags';
import { getLists, addListItem } from '../../api/lists';
import { useProfile } from '../../context/ProfileContext';
import type { FlagResponse, ListResponse } from '../../types';
import LogWatchModal from './LogWatchModal';

interface Props {
  titleId: number;
  titleName: string;
}

export default function MovieActions({ titleId, titleName }: Props) {
  const { activeProfile } = useProfile();
  const [showLogModal, setShowLogModal] = useState(false);
  const [flag, setFlag] = useState<FlagResponse | null>(null);
  const [lists, setLists] = useState<ListResponse[]>([]);
  const [showListMenu, setShowListMenu] = useState(false);
  const [addedMessage, setAddedMessage] = useState('');

  const profileId = activeProfile?.id;

  useEffect(() => {
    if (!profileId) return;
    getFlags(profileId).then((flags) => {
      const f = flags.find((f) => f.title_id === titleId);
      setFlag(f || null);
    });
    getLists(profileId).then(setLists);
  }, [profileId, titleId]);

  if (!profileId) return null;

  const handleFlag = async () => {
    if (flag) {
      await deleteFlag(profileId, titleId);
      setFlag(null);
    } else {
      const f = await createFlag(profileId, titleId, 'not_interested');
      setFlag(f);
    }
  };

  const handleAddToList = async (listId: number, listName: string) => {
    try {
      await addListItem(profileId, listId, titleId);
      setAddedMessage(`Added to ${listName}`);
      setTimeout(() => setAddedMessage(''), 2000);
    } catch {
      setAddedMessage('Already in list');
      setTimeout(() => setAddedMessage(''), 2000);
    }
    setShowListMenu(false);
  };

  return (
    <div className="flex flex-wrap items-center gap-3 mt-4">
      <button
        onClick={() => setShowLogModal(true)}
        className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold"
      >
        Mark Watched
      </button>

      <div className="relative">
        <button
          onClick={() => setShowListMenu(!showListMenu)}
          className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white"
        >
          Add to List
        </button>
        {showListMenu && (
          <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-10 min-w-48">
            {lists.length === 0 ? (
              <div className="px-4 py-2 text-sm text-gray-400">
                No lists yet
              </div>
            ) : (
              lists.map((list) => (
                <button
                  key={list.id}
                  onClick={() => handleAddToList(list.id, list.name)}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-200 hover:bg-gray-700"
                >
                  {list.name}
                </button>
              ))
            )}
          </div>
        )}
      </div>

      <button
        onClick={handleFlag}
        className={`px-4 py-2 rounded ${
          flag
            ? 'bg-red-900 text-red-300 hover:bg-red-800'
            : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
        }`}
      >
        {flag ? 'Not Interested (undo)' : 'Not Interested'}
      </button>

      {addedMessage && (
        <span className="text-sm text-green-400">{addedMessage}</span>
      )}

      {showLogModal && (
        <LogWatchModal
          titleId={titleId}
          titleName={titleName}
          profileId={profileId}
          onClose={() => setShowLogModal(false)}
          onSaved={() => {}}
        />
      )}
    </div>
  );
}
