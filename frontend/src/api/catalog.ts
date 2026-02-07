import type {
  BrowseResponse,
  CollectionBrief,
  CollectionDetail,
  FeaturedRowsResponse,
  LanguageListResponse,
  PaginatedSearchResponse,
  PersonWithFilmography,
  ProviderListResponse,
  RandomMovie,
  SimilarTitle,
  SortOption,
  TitleDetailResponse,
  WatchProvider,
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
  genres?: string[];
  minYear?: number;
  maxYear?: number;
  decade?: number;
  minRating?: number;
  minRuntime?: number;
  maxRuntime?: number;
  language?: string;
  sortBy?: SortOption;
  excludeWatchedProfileId?: number;
  providerIds?: number[];
}

export async function browseCatalog(
  page: number = 1,
  limit: number = 20,
  filters?: BrowseFilters
): Promise<BrowseResponse> {
  const params: Record<string, string | number> = { page, limit };
  if (filters?.genres?.length) params.genres = filters.genres.join(',');
  else if (filters?.genre) params.genre = filters.genre;
  if (filters?.minYear) params.min_year = filters.minYear;
  if (filters?.maxYear) params.max_year = filters.maxYear;
  if (filters?.decade) params.decade = filters.decade;
  if (filters?.minRating) params.min_rating = filters.minRating;
  if (filters?.minRuntime) params.min_runtime = filters.minRuntime;
  if (filters?.maxRuntime) params.max_runtime = filters.maxRuntime;
  if (filters?.language) params.language = filters.language;
  if (filters?.sortBy) params.sort_by = filters.sortBy;
  if (filters?.excludeWatchedProfileId) params.exclude_watched = filters.excludeWatchedProfileId;
  if (filters?.providerIds?.length) params.provider_ids = filters.providerIds.join(',');
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

export interface RandomMovieFilters {
  genre?: string;
  decade?: number;
  minRating?: number;
  excludeWatchedProfileId?: number;
}

export async function getRandomMovie(filters?: RandomMovieFilters): Promise<RandomMovie> {
  const params: Record<string, string | number> = {};
  if (filters?.genre) params.genre = filters.genre;
  if (filters?.decade) params.decade = filters.decade;
  if (filters?.minRating) params.min_rating = filters.minRating;
  if (filters?.excludeWatchedProfileId) params.exclude_watched = filters.excludeWatchedProfileId;
  const { data } = await api.get<RandomMovie>('/catalog/random', { params });
  return data;
}

export async function getFeaturedRows(
  limit: number = 20,
  excludeWatchedProfileId?: number
): Promise<FeaturedRowsResponse> {
  const params: Record<string, string | number> = { limit };
  if (excludeWatchedProfileId) params.exclude_watched = excludeWatchedProfileId;
  const { data } = await api.get<FeaturedRowsResponse>('/catalog/featured-rows', { params });
  return data;
}

export async function getFeaturedGenres(): Promise<string[]> {
  const { data } = await api.get<{ genres: string[] }>('/catalog/featured-genres');
  return data.genres;
}

export async function getLanguages(): Promise<LanguageListResponse> {
  const { data } = await api.get<LanguageListResponse>('/catalog/languages');
  return data;
}

export async function getProviders(): Promise<ProviderListResponse> {
  const { data } = await api.get<ProviderListResponse>('/catalog/providers');
  return data;
}

export async function getTitleProviders(titleId: number): Promise<WatchProvider[]> {
  const { data } = await api.get<WatchProvider[]>(`/catalog/titles/${titleId}/providers`);
  return data;
}
