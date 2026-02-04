import type { Profile } from '../types';
import api from './client';

export async function getProfiles(): Promise<Profile[]> {
  const { data } = await api.get<Profile[]>('/profiles');
  return data;
}

export async function createProfile(name: string): Promise<Profile> {
  const { data } = await api.post<Profile>('/profiles', { name });
  return data;
}
