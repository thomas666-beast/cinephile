import { api } from "./client";
import type {
  HomeResponse, MovieDetail, MovieListItem, Paginated,
  SeriesDetail, SeriesListItem, Genre, MeResponse,
  SubscriptionPlan, SubscriptionResponse, PlaybackResponse,
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
  me: () => api.get<SubscriptionResponse>("/subscriptions/me/").then(r => r.data),
};

export const playbackApi = {
  movie: (slug: string) =>
    api.post<PlaybackResponse>(`/playback/movies/${slug}/`).then(r => r.data),
  episode: (id: number) =>
    api.post<PlaybackResponse>(`/playback/episodes/${id}/`).then(r => r.data),
};
