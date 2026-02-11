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
  rt_critic_score?: number | null;
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
  rt_critic_score: number | null;
  rt_audience_score: number | null;
  metacritic_score: number | null;
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
  overview: string | null;
  trailer_key: string | null;
  original_language: string | null;
  rating: RatingResponse | null;
  rt_critic_score: number | null;
  rt_audience_score: number | null;
  metacritic_score: number | null;
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
  mood?: string;
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
  rt_critic_score: number | null;
}

export interface RecommendResponse {
  results: RecommendedTitle[];
  total: number;
  page: number;
  limit: number;
  fallback_mode: boolean;
  mood_mode: boolean;
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
  rt_critic_score?: number | null;
}

export interface OnboardingMoviesResponse {
  movies: OnboardingMovie[];
  remaining: number;
}

// Browse/Discovery types
export type SortOption = 'popularity' | 'rating' | 'year_desc' | 'year_asc';

export interface BrowseTitle {
  id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
  rt_critic_score: number | null;
}

export interface BrowseResponse {
  results: BrowseTitle[];
  total: number;
  page: number;
  limit: number;
}

export interface SimilarTitle {
  id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  similarity_score: number;
  poster_url: string | null;
  rt_critic_score?: number | null;
}

export interface PersonDetail {
  id: number;
  imdb_nconst: string;
  primary_name: string;
  birth_year: number | null;
  death_year: number | null;
}

export interface FilmographyItem {
  title_id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  genres: string | null;
  category: string;
  characters: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
  rt_critic_score?: number | null;
}

export interface PersonWithFilmography {
  person: PersonDetail;
  filmography: FilmographyItem[];
}

// Collection types
export interface CollectionBrief {
  id: number;
  name: string;
  description: string | null;
  collection_type: string;
}

export interface CollectionTitle {
  title_id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
  position: number | null;
  rt_critic_score?: number | null;
}

export interface CollectionDetail {
  id: number;
  name: string;
  description: string | null;
  collection_type: string;
  results: CollectionTitle[];
  total: number;
  page: number;
  limit: number;
}

// Random movie and featured rows types
export interface RandomMovie {
  id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
  overview: string | null;
}

export interface FeaturedRowMovie {
  id: number;
  imdb_tconst: string;
  primary_title: string;
  start_year: number | null;
  runtime_minutes: number | null;
  genres: string | null;
  average_rating: number | null;
  num_votes: number | null;
  poster_url: string | null;
  rt_critic_score: number | null;
}

export interface FeaturedRow {
  id: string;
  title: string;
  movies: FeaturedRowMovie[];
}

export interface FeaturedRowsResponse {
  rows: FeaturedRow[];
}

// Language types
export interface LanguageOption {
  code: string;
  count: number;
}

export interface LanguageListResponse {
  languages: LanguageOption[];
}

// Watch provider types
export interface WatchProvider {
  id: number;
  provider_id: number;
  provider_name: string;
  logo_path: string | null;
  provider_type: 'flatrate' | 'rent' | 'buy';
  region: string;
  display_priority: number | null;
}

export interface ProviderMaster {
  provider_id: number;
  provider_name: string;
  logo_path: string | null;
  display_priority: number | null;
  movie_count?: number;
}

export interface ProviderListResponse {
  providers: ProviderMaster[];
}

// Stats types
export interface RatingBucket {
  rating: number;
  count: number;
}

export interface GenreCount {
  genre: string;
  count: number;
}

export interface PersonStat {
  person_id: number;
  name: string;
  count: number;
  avg_rating: number | null;
}

export interface CriticComparison {
  title_id: number;
  primary_title: string;
  user_score: number;
  critic_score: number;
}

export interface MonthCount {
  month: string;
  count: number;
}

export interface MonthRating {
  month: string;
  avg_rating: number;
}

export interface DecadeCount {
  decade: number;
  count: number;
}

export interface RatedMovie {
  title_id: number;
  primary_title: string;
  start_year: number | null;
  rating: number;
  poster_url: string | null;
}

export interface LanguageCount {
  language: string;
  count: number;
}

export interface ProfileStats {
  total_movies: number;
  avg_rating: number | null;
  total_runtime_minutes: number;
  unique_languages: number;
  total_rewatches: number;
  rating_distribution: RatingBucket[];
  genre_breakdown: GenreCount[];
  top_directors: PersonStat[];
  top_actors: PersonStat[];
  critic_comparisons: CriticComparison[];
  avg_user_score: number | null;
  avg_critic_score: number | null;
  avg_difference: number | null;
  movies_per_month: MonthCount[];
  rating_over_time: MonthRating[];
  decade_distribution: DecadeCount[];
  highest_rated: RatedMovie[];
  lowest_rated: RatedMovie[];
  language_diversity: LanguageCount[];
}
