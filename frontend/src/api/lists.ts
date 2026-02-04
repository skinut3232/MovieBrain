import type {
  ListDetailResponse,
  ListItemResponse,
  ListResponse,
  ListType,
} from '../types';
import api from './client';

export async function getLists(profileId: number): Promise<ListResponse[]> {
  const { data } = await api.get<ListResponse[]>(
    `/profiles/${profileId}/lists`
  );
  return data;
}

export async function createList(
  profileId: number,
  name: string,
  listType: ListType = 'custom'
): Promise<ListResponse> {
  const { data } = await api.post<ListResponse>(
    `/profiles/${profileId}/lists`,
    { name, list_type: listType }
  );
  return data;
}

export async function getListDetail(
  profileId: number,
  listId: number
): Promise<ListDetailResponse> {
  const { data } = await api.get<ListDetailResponse>(
    `/profiles/${profileId}/lists/${listId}`
  );
  return data;
}

export async function updateList(
  profileId: number,
  listId: number,
  name: string
): Promise<ListResponse> {
  const { data } = await api.patch<ListResponse>(
    `/profiles/${profileId}/lists/${listId}`,
    { name }
  );
  return data;
}

export async function deleteList(
  profileId: number,
  listId: number
): Promise<void> {
  await api.delete(`/profiles/${profileId}/lists/${listId}`);
}

export async function addListItem(
  profileId: number,
  listId: number,
  titleId: number,
  priority?: number
): Promise<ListItemResponse> {
  const { data } = await api.post<ListItemResponse>(
    `/profiles/${profileId}/lists/${listId}/items`,
    { title_id: titleId, priority }
  );
  return data;
}

export async function reorderListItems(
  profileId: number,
  listId: number,
  orderedTitleIds: number[]
): Promise<void> {
  await api.patch(`/profiles/${profileId}/lists/${listId}/items/reorder`, {
    ordered_title_ids: orderedTitleIds,
  });
}

export async function removeListItem(
  profileId: number,
  listId: number,
  titleId: number
): Promise<void> {
  await api.delete(
    `/profiles/${profileId}/lists/${listId}/items/${titleId}`
  );
}
