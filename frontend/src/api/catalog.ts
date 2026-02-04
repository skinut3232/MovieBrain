import type { PaginatedSearchResponse, TitleDetailResponse } from '../types';
import api from './client';

export async function searchTitles(
  query: string,
  page: number = 1,
  year?: number
): Promise<PaginatedSearchResponse> {
  const params: Record<string, string | number> = { q: query, page };
  if (year) params.year = year;
  const { data } = await api.get<PaginatedSearchResponse>('/catalog/search', { params });
  return data;
}

export async function getTitleDetail(titleId: number): Promise<TitleDetailResponse> {
  const { data } = await api.get<TitleDetailResponse>(`/catalog/titles/${titleId}`);
  return data;
}
