export interface Genre {
  id: number;
  name: string;
  slug: string;
}

export interface MovieListItem {
  id: number;
  title: string;
  slug: string;
  release_year: number | null;
  duration_minutes: number | null;
  poster: string | null;
  genres: Genre[];
  published_at: string;
}

export interface MovieDetail extends MovieListItem {
  synopsis: string;
  backdrop: string | null;
  created_at: string;
  updated_at: string;
}

export interface EpisodeItem {
  id: number;
  number: number;
  title: string;
  synopsis: string;
  duration_minutes: number | null;
  still: string | null;
  air_date: string | null;
}

export interface SeasonItem {
  id: number;
  number: number;
  title: string;
  synopsis: string;
  poster: string | null;
  episodes: EpisodeItem[];
}

export interface SeriesListItem {
  id: number;
  title: string;
  slug: string;
  start_year: number | null;
  end_year: number | null;
  poster: string | null;
  genres: Genre[];
  published_at: string;
}

export interface SeriesDetail extends SeriesListItem {
  synopsis: string;
  backdrop: string | null;
  seasons: SeasonItem[];
  created_at: string;
  updated_at: string;
}

export interface HomeResponse {
  latest_movies: MovieListItem[];
  latest_series: SeriesListItem[];
}

export interface PlaybackResponse {
  token: string;
  content_type: "movie" | "episode";
  content_id: number;
  expires_in_seconds: number;
  hls_manifest_url: string | null;
  duration_seconds: number | null;
  renditions: string[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface MeResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "admin" | "viewer";
  is_staff: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface SubscriptionPlan {
  id: number;
  name: string;
  slug: string;
  description: string;
  price_cents: number;
  currency: string;
  billing_period: "monthly" | "yearly";
  duration_days: number;
}

export interface SubscriptionResponse {
  id: number;
  plan: SubscriptionPlan;
  status: "active" | "expired" | "canceled";
  started_at: string;
  expires_at: string;
  canceled_at: string | null;
  created_at: string;
}

export interface SearchResponse {
  query: string;
  type: "all" | "movie" | "series";
  movies: { count: number; results: MovieListItem[] };
  series: { count: number; results: SeriesListItem[] };
}
