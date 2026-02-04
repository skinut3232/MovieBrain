import type { FlagResponse, FlagType } from '../types';
import api from './client';

export async function createFlag(
  profileId: number,
  titleId: number,
  flagType: FlagType
): Promise<FlagResponse> {
  const { data } = await api.post<FlagResponse>(
    `/profiles/${profileId}/flags`,
    { title_id: titleId, flag_type: flagType }
  );
  return data;
}

export async function deleteFlag(
  profileId: number,
  titleId: number
): Promise<void> {
  await api.delete(`/profiles/${profileId}/flags/${titleId}`);
}

export async function getFlags(
  profileId: number,
  flagType?: FlagType
): Promise<FlagResponse[]> {
  const params = flagType ? { flag_type: flagType } : {};
  const { data } = await api.get<FlagResponse[]>(
    `/profiles/${profileId}/flags`,
    { params }
  );
  return data;
}
