import { useEffect, useState, useCallback } from 'react';
import { createFlag, deleteFlag, getFlags } from '../../api/flags';
import { getLists, addListItem } from '../../api/lists';
import { useProfile } from '../../context/ProfileContext';
import type { FlagResponse, ListResponse } from '../../types';
import LogWatchModal from './LogWatchModal';

interface Props {
  titleId: number;
  titleName: string;
  trailerKey?: string | null;
}

export default function MovieActions({ titleId, titleName, trailerKey }: Props) {
  const { activeProfile } = useProfile();
  const [showLogModal, setShowLogModal] = useState(false);
  const [showTrailer, setShowTrailer] = useState(false);
  const [flag, setFlag] = useState<FlagResponse | null>(null);
  const [lists, setLists] = useState<ListResponse[]>([]);
  const [showListMenu, setShowListMenu] = useState(false);
  const [addedMessage, setAddedMessage] = useState('');

  const closeTrailer = useCallback(() => setShowTrailer(false), []);

  useEffect(() => {
    if (!showTrailer) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeTrailer();
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [showTrailer, closeTrailer]);

  const profileId = activeProfile?.id;

  useEffect(() => {
    if (!profileId) return;
    let cancelled = false;
    getFlags(profileId).then((flags) => {
      if (!cancelled) {
        const f = flags.find((f) => f.title_id === titleId);
        setFlag(f || null);
      }
    });
    getLists(profileId).then((l) => {
      if (!cancelled) setLists(l);
    });
    return () => { cancelled = true; };
  }, [profileId, titleId]);

  if (!profileId) return null;

  const handleFlag = async () => {
    try {
      if (flag) {
        await deleteFlag(profileId, titleId);
        setFlag(null);
      } else {
        const f = await createFlag(profileId, titleId, 'not_interested');
        setFlag(f);
      }
    } catch {
      // Flag toggle failed — state unchanged, no action needed
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

      {trailerKey && (
        <>
          <div className="basis-full h-0" />
          <button
            onClick={() => setShowTrailer(true)}
            className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white"
          >
            Watch Trailer
          </button>
        </>
      )}

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

      {showTrailer && trailerKey && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
          onClick={closeTrailer}
        >
          <div
            className="relative w-full max-w-4xl mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={closeTrailer}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 text-3xl leading-none"
              aria-label="Close trailer"
            >
              &times;
            </button>
            <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
              <iframe
                className="absolute inset-0 w-full h-full rounded-lg"
                src={`https://www.youtube.com/embed/${trailerKey}?autoplay=1`}
                title={`${titleName} trailer`}
                allow="autoplay; encrypted-media"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
