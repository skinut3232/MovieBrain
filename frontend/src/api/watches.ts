import type { PaginatedWatchHistory, ProfileStats, Tag, WatchCreate, WatchResponse } from '../types';
import api from './client';

export async function logWatch(
  profileId: number,
  body: WatchCreate
): Promise<WatchResponse> {
  const { data } = await api.post<WatchResponse>(
    `/profiles/${profileId}/watches`,
    body
  );
  return data;
}

export async function getWatchHistory(
  profileId: number,
  params: {
    page?: number;
    limit?: number;
    sort_by?: string;
    tag?: string;
    min_rating?: number;
    max_rating?: number;
  } = {}
): Promise<PaginatedWatchHistory> {
  const { data } = await api.get<PaginatedWatchHistory>(
    `/profiles/${profileId}/history`,
    { params }
  );
  return data;
}

export async function deleteWatch(
  profileId: number,
  titleId: number
): Promise<void> {
  await api.delete(`/profiles/${profileId}/watches/${titleId}`);
}

export async function getTags(profileId: number): Promise<Tag[]> {
  const { data } = await api.get<Tag[]>(`/profiles/${profileId}/tags`);
  return data;
}

export async function createTag(
  profileId: number,
  name: string
): Promise<Tag> {
  const { data } = await api.post<Tag>(`/profiles/${profileId}/tags`, { name });
  return data;
}

export async function deleteTag(
  profileId: number,
  tagId: number
): Promise<void> {
  await api.delete(`/profiles/${profileId}/tags/${tagId}`);
}

export async function getProfileStats(
  profileId: number
): Promise<ProfileStats> {
  const { data } = await api.get<ProfileStats>(
    `/profiles/${profileId}/stats`
  );
  return data;
}
