import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getListDetail, removeListItem, deleteList } from '../../api/lists';
import { useProfile } from '../../context/ProfileContext';
import type { ListDetailResponse } from '../../types';
import ListItemRow from './ListItem';

export default function ListDetail() {
  const { listId } = useParams<{ listId: string }>();
  const { activeProfile } = useProfile();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<ListDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const profileId = activeProfile?.id;

  const loadDetail = useCallback(async () => {
    if (!profileId || !listId) return;
    setLoading(true);
    try {
      const data = await getListDetail(profileId, Number(listId));
      setDetail(data);
    } finally {
      setLoading(false);
    }
  }, [profileId, listId]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  const handleRemoveItem = async (titleId: number) => {
    if (!profileId || !listId) return;
    await removeListItem(profileId, Number(listId), titleId);
    loadDetail();
  };

  const handleDeleteList = async () => {
    if (!profileId || !listId || !confirm('Delete this list?')) return;
    await deleteList(profileId, Number(listId));
    navigate('/lists');
  };

  if (loading) return <p className="text-gray-400">Loading...</p>;
  if (!detail) return <p className="text-gray-400">List not found.</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-white">{detail.name}</h1>
          <p className="text-sm text-gray-400">
            {detail.list_type} &middot; {detail.items.length} item
            {detail.items.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button
          onClick={handleDeleteList}
          className="px-3 py-1.5 rounded bg-red-900 text-red-300 hover:bg-red-800 text-sm"
        >
          Delete List
        </button>
      </div>

      {detail.items.length === 0 ? (
        <p className="text-gray-500">No items in this list yet.</p>
      ) : (
        <div className="grid gap-2">
          {detail.items.map((item) => (
            <ListItemRow
              key={item.title_id}
              item={item}
              onRemove={handleRemoveItem}
            />
          ))}
        </div>
      )}
    </div>
  );
}
