import { api } from "./client";
import type {
  HomeResponse, MovieDetail, MovieListItem, Paginated,
  SeriesDetail, SeriesListItem, Genre, MeResponse,
  SubscriptionPlan, SubscriptionResponse, PlaybackResponse, SearchResponse
} from "./types";

export const catalogApi = {
  home: () => api.get<HomeResponse>("/home/").then(r => r.data),
  movies: (params?: Record<string, unknown>) =>
    api.get<Paginated<MovieListItem>>("/movies/", { params }).then(r => r.data),
  movie: (slug: string) =>
    api.get<MovieDetail>(`/movies/${slug}/`).then(r => r.data),
  seriesList: (params?: Record<string, unknown>) =>
    api.get<Paginated<SeriesListItem>>("/series/", { params }).then(r => r.data),
  series: (slug: string) =>
    api.get<SeriesDetail>(`/series/${slug}/`).then(r => r.data),
  genres: () => api.get<Genre[]>("/genres/").then(r => r.data),
  search: (q: string, type: "all" | "movie" | "series" = "all", page = 1) =>
      api.get<SearchResponse>("/search/", { params: { q, type, page } }).then(r => r.data),
};

export const authApi = {
  register: (body: { email: string; password: string; password_confirm: string;
                     first_name?: string; last_name?: string }) =>
    api.post("/auth/register/", body).then(r => r.data),
  login: (body: { email: string; password: string }) =>
    api.post<{ access: string; refresh: string }>("/auth/token/", body).then(r => r.data),
  logout: (refresh: string) =>
    api.post("/auth/logout/", { refresh }).then(r => r.data),
  me: () => api.get<MeResponse>("/auth/me/").then(r => r.data),
};

export const subscriptionApi = {
  plans: () => api.get<SubscriptionPlan[]>("/plans/").then(r => r.data),
  subscribe: (plan_slug: string) =>
    api.post<SubscriptionResponse>("/subscriptions/", { plan_slug }).then(r => r.data),
  me: () =>
    // 404 is expected when there's no active subscription; handle in caller
    api.get<SubscriptionResponse>("/subscriptions/me/").then(r => r.data),
  cancel: (id: number) =>
    api.post<SubscriptionResponse>(`/subscriptions/${id}/cancel/`).then(r => r.data),
};

export const playbackApi = {
  movie: (slug: string) =>
    api.post<PlaybackResponse>(`/playback/movies/${slug}/`).then(r => r.data),
  episode: (id: number) =>
    api.post<PlaybackResponse>(`/playback/episodes/${id}/`).then(r => r.data),
};

export interface AdminMoviePayload {
  title: string;
  synopsis?: string;
  release_year?: number | null;
  duration_minutes?: number | null;
  genres?: number[];
  status?: "draft" | "published";
}

export interface AdminSeriesPayload {
  title: string;
  synopsis?: string;
  start_year?: number | null;
  end_year?: number | null;
  genres?: number[];
  status?: "draft" | "published";
}

export const adminApi = {
  stats: () => api.get("/admin/stats/").then(r => r.data),

  // Movies
  listMovies: (params?: { search?: string; status?: string; page?: number }) =>
    api.get("/admin/movies/", { params }).then(r => r.data),
  getMovie: (slug: string) => api.get(`/admin/movies/${slug}/`).then(r => r.data),
  createMovie: (body: AdminMoviePayload) =>
    api.post("/admin/movies/", body).then(r => r.data),
  updateMovie: (slug: string, body: Partial<AdminMoviePayload>) =>
    api.patch(`/admin/movies/${slug}/`, body).then(r => r.data),
  deleteMovie: (slug: string) => api.delete(`/admin/movies/${slug}/`).then(r => r.data),
  publishMovie: (slug: string) => api.post(`/admin/movies/${slug}/publish/`).then(r => r.data),
  unpublishMovie: (slug: string) => api.post(`/admin/movies/${slug}/unpublish/`).then(r => r.data),
  uploadMoviePoster: (slug: string, file: File) => {
    const fd = new FormData();
    fd.append("poster", file);
    return api.patch(`/admin/movies/${slug}/`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then(r => r.data);
  },
  uploadMovieBackdrop: (slug: string, file: File) => {
    const fd = new FormData();
    fd.append("backdrop", file);
    return api.patch(`/admin/movies/${slug}/`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then(r => r.data);
  },

  // Series
  listSeries: (params?: { search?: string; status?: string; page?: number }) =>
    api.get("/admin/series/", { params }).then(r => r.data),
  getSeries: (slug: string) => api.get(`/admin/series/${slug}/`).then(r => r.data),
  createSeries: (body: AdminSeriesPayload) =>
    api.post("/admin/series/", body).then(r => r.data),
  updateSeries: (slug: string, body: Partial<AdminSeriesPayload>) =>
    api.patch(`/admin/series/${slug}/`, body).then(r => r.data),
  deleteSeries: (slug: string) => api.delete(`/admin/series/${slug}/`).then(r => r.data),
  publishSeries: (slug: string) => api.post(`/admin/series/${slug}/publish/`).then(r => r.data),
  unpublishSeries: (slug: string) => api.post(`/admin/series/${slug}/unpublish/`).then(r => r.data),

  // Seasons & episodes
  listSeasons: (seriesSlug: string) =>
    api.get("/admin/seasons/", { params: { series__slug: seriesSlug } }).then(r => r.data),
  createSeason: (body: { series: string; number: number; title?: string; synopsis?: string }) =>
    api.post("/admin/seasons/", body).then(r => r.data),
  updateSeason: (id: number, body: Partial<{ number: number; title: string; synopsis: string }>) =>
    api.patch(`/admin/seasons/${id}/`, body).then(r => r.data),
  deleteSeason: (id: number) => api.delete(`/admin/seasons/${id}/`).then(r => r.data),
  createEpisode: (body: {
    season: number; number: number; title: string;
    synopsis?: string; duration_minutes?: number | null; air_date?: string | null;
    status?: "draft" | "published";
  }) => api.post("/admin/episodes/", body).then(r => r.data),
  updateEpisode: (id: number, body: Partial<{ number: number; title: string; status: string }>) =>
    api.patch(`/admin/episodes/${id}/`, body).then(r => r.data),
  deleteEpisode: (id: number) => api.delete(`/admin/episodes/${id}/`).then(r => r.data),

  // Genres
  listGenres: () => api.get("/admin/genres/").then(r => r.data),
  createGenre: (body: { name: string }) => api.post("/admin/genres/", body).then(r => r.data),
  deleteGenre: (id: number) => api.delete(`/admin/genres/${id}/`).then(r => r.data),

  // Video upload + status
  uploadVideo: (
    movieId: number,
    file: File,
    mimeType: string,
    onProgress: (pct: number) => void,
  ) => {
    const fd = new FormData();
    fd.append("movie", String(movieId));
    fd.append("video_file", file);
    fd.append("mime_type", mimeType);
    return api.post("/admin/videos/", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (e.total) onProgress(Math.round((e.loaded / e.total) * 100));
      },
    }).then(r => r.data);
  },
};

export interface WatchProgressResponse {
  id: number;
  content_type: "movie" | "episode";
  content_id: number;
  title: string;
  poster: string | null;
  slug: string;
  progress_seconds: number;
  duration_seconds: number;
  percent: number;
  updated_at: string;
}

export const historyApi = {
  save: (data: {
    profile_id: number;
    content_type: string;
    content_id: number;
    progress_seconds: number;
    duration_seconds: number;
  }) => api.post("/history/progress/", data).then(r => r.data),
  list: (profileId: number) =>
    api.get<WatchProgressResponse[]>("/history/", { params: { profile_id: profileId } })
      .then(r => r.data),
};

export const passwordApi = {
  requestReset: (email: string) =>
    api.post("/auth/password-reset/", { email }).then(r => r.data),
  confirmReset: (data: { uid: string; token: string; new_password: string; confirm_password: string }) =>
    api.post("/auth/password-reset/confirm/", data).then(r => r.data),
};
