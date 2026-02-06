import type {
  BrowseResponse,
  CollectionBrief,
  CollectionDetail,
  PaginatedSearchResponse,
  PersonWithFilmography,
  SimilarTitle,
  SortOption,
  TitleDetailResponse,
} from '../types';
import api from './client';

export interface SearchFilters {
  genre?: string;
  minRating?: number;
  minYear?: number;
  maxYear?: number;
}

export async function searchTitles(
  query: string,
  page: number = 1,
  filters?: SearchFilters
): Promise<PaginatedSearchResponse> {
  const params: Record<string, string | number> = { q: query, page };
  if (filters?.genre) params.genre = filters.genre;
  if (filters?.minRating) params.min_rating = filters.minRating;
  if (filters?.minYear) params.min_year = filters.minYear;
  if (filters?.maxYear) params.max_year = filters.maxYear;
  const { data } = await api.get<PaginatedSearchResponse>('/catalog/search', { params });
  return data;
}

export async function getTitleDetail(titleId: number): Promise<TitleDetailResponse> {
  const { data } = await api.get<TitleDetailResponse>(`/catalog/titles/${titleId}`);
  return data;
}

export interface BrowseFilters {
  genre?: string;
  minYear?: number;
  maxYear?: number;
  decade?: number;
  minRating?: number;
  sortBy?: SortOption;
}

export async function browseCatalog(
  page: number = 1,
  limit: number = 20,
  filters?: BrowseFilters
): Promise<BrowseResponse> {
  const params: Record<string, string | number> = { page, limit };
  if (filters?.genre) params.genre = filters.genre;
  if (filters?.minYear) params.min_year = filters.minYear;
  if (filters?.maxYear) params.max_year = filters.maxYear;
  if (filters?.decade) params.decade = filters.decade;
  if (filters?.minRating) params.min_rating = filters.minRating;
  if (filters?.sortBy) params.sort_by = filters.sortBy;
  const { data } = await api.get<BrowseResponse>('/catalog/browse', { params });
  return data;
}

export async function getGenres(): Promise<string[]> {
  const { data } = await api.get<{ genres: string[] }>('/catalog/genres');
  return data.genres;
}

export async function getDecades(): Promise<number[]> {
  const { data } = await api.get<{ decades: number[] }>('/catalog/decades');
  return data.decades;
}

export async function getSimilarMovies(titleId: number, limit: number = 10): Promise<SimilarTitle[]> {
  const { data } = await api.get<SimilarTitle[]>(`/catalog/titles/${titleId}/similar`, {
    params: { limit },
  });
  return data;
}

export async function getPersonWithFilmography(personId: number): Promise<PersonWithFilmography> {
  const { data } = await api.get<PersonWithFilmography>(`/catalog/people/${personId}`);
  return data;
}

export async function getCollections(): Promise<CollectionBrief[]> {
  const { data } = await api.get<CollectionBrief[]>('/collections');
  return data;
}

export async function getCollectionDetail(
  collectionId: number,
  page: number = 1,
  limit: number = 20
): Promise<CollectionDetail> {
  const { data } = await api.get<CollectionDetail>(`/collections/${collectionId}`, {
    params: { page, limit },
  });
  return data;
}
