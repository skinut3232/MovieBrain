import type { RecommendRequest, RecommendResponse, TasteProfileResponse } from '../types';
import api from './client';

export async function getRecommendations(
  profileId: number,
  filters: RecommendRequest = {}
): Promise<RecommendResponse> {
  const { data } = await api.post<RecommendResponse>(
    `/profiles/${profileId}/recommend`,
    filters
  );
  return data;
}

export async function getTasteProfile(
  profileId: number
): Promise<TasteProfileResponse> {
  const { data } = await api.get<TasteProfileResponse>(
    `/profiles/${profileId}/taste`
  );
  return data;
}

export async function recomputeTaste(
  profileId: number
): Promise<TasteProfileResponse> {
  const { data } = await api.post<TasteProfileResponse>(
    `/profiles/${profileId}/taste/recompute`
  );
  return data;
}
