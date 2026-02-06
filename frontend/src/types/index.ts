export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Profile {
  id: number;
  name: string;
  onboarding_completed: boolean;
  created_at: string;
}

export interface TitleBrief {
  id: number;
  primary_title: string;
  start_year: number | null;
  genres: string | null;
  poster_url: string | null;
}

export interface TitleSearchResult {
  id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
}

export interface PaginatedSearchResponse {
  results: TitleSearchResult[];
  total: number;
  page: number;
  limit: number;
}

export interface PersonBrief {
  id: number;
  imdb_nconst: string;
  primary_name: string;
}

export interface PrincipalResponse {
  ordering: number | null;
  category: string | null;
  job: string | null;
  characters: string | null;
  person: PersonBrief;
}

export interface RatingResponse {
  average_rating: number | null;
  num_votes: number | null;
}

export interface CrewResponse {
  director_nconsts: string[] | null;
  writer_nconsts: string[] | null;
}

export interface AkaResponse {
  localized_title: string | null;
  region: string | null;
  language: string | null;
  is_original: boolean | null;
}

export interface TitleDetailResponse {
  id: number;
  imdb_tconst: string;
  title_type: string | null;
  primary_title: string;
  original_title: string | null;
  start_year: number | null;
  end_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  poster_url: string | null;
  rating: RatingResponse | null;
  principals: PrincipalResponse[];
  crew: CrewResponse | null;
  akas: AkaResponse[];
}

export interface Tag {
  id: number;
  name: string;
}

export interface WatchResponse {
  id: number;
  title_id: number;
  rating_1_10: number | null;
  notes: string | null;
  rewatch_count: number;
  watched_date: string | null;
  created_at: string;
  updated_at: string;
  title: TitleBrief;
  tags: Tag[];
}

export interface PaginatedWatchHistory {
  results: WatchResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface WatchCreate {
  title_id: number;
  rating_1_10?: number | null;
  notes?: string | null;
  rewatch_count?: number;
  watched_date?: string | null;
  tag_names?: string[];
}

export type ListType = 'watchlist' | 'favorites' | 'rewatch' | 'custom';

export interface ListResponse {
  id: number;
  name: string;
  list_type: ListType;
  created_at: string;
  updated_at: string;
  item_count: number;
}

export interface ListItemResponse {
  title_id: number;
  position: number;
  priority: number | null;
  added_at: string;
  title: TitleBrief;
}

export interface ListDetailResponse {
  id: number;
  name: string;
  list_type: ListType;
  created_at: string;
  updated_at: string;
  items: ListItemResponse[];
}

export type FlagType = 'not_interested' | 'dont_recommend';

export interface FlagResponse {
  id: number;
  title_id: number;
  flag_type: FlagType;
  created_at: string;
}

// Recommendation types
export interface RecommendRequest {
  genre?: string;
  min_year?: number;
  max_year?: number;
  min_runtime?: number;
  max_runtime?: number;
  min_imdb_rating?: number;
  min_votes?: number;
  limit?: number;
  page?: number;
}

export interface RecommendedTitle {
  title_id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  similarity_score: number | null;
  poster_url: string | null;
}

export interface RecommendResponse {
  results: RecommendedTitle[];
  total: number;
  page: number;
  limit: number;
  fallback_mode: boolean;
}

export interface TasteProfileResponse {
  has_taste_vector: boolean;
  num_rated_movies: number;
  min_required: number;
  updated_at: string | null;
}

// Onboarding types
export interface OnboardingMovie {
  title_id: number;
  primary_title: string;
  start_year: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
}

export interface OnboardingMoviesResponse {
  movies: OnboardingMovie[];
  remaining: number;
}
