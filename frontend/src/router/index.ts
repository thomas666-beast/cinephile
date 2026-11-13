import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/HomeView.vue"),
    },
    {
        path: "/movies",
        name: "movies",
        component: () => import("../views/MoviesView.vue"),
    },
    {
        path: "/movies/:slug",
        name: "movie-detail",
        component: () => import("../views/MovieDetailView.vue"),
    },
    {
        path: "/series",
        name: "series",
        component: () => import("../views/SeriesView.vue"),
    },
    {
        path: "/series/:slug",
        name: "series-detail",
        component: () => import("../views/SeriesDetailView.vue"),
    },
    {
        path: "/sign-in",
        name: "sign-in",
        component: () => import("../views/SignInView.vue"),
    },
    {
        path: "/register",
        name: "register",
        component: () => import("../views/RegisterView.vue"),
    },
    {
      path: "/plans",
      name: "plans",
      component: () => import("../views/PlansView.vue"),
    },
    {
      path: "/my-account",
      name: "my-account",
      component: () => import("../views/MyAccountView.vue"),
    },
    {
      path: "/watch/movie/:slug",
      name: "watch-movie",
      component: () => import("../views/WatchMovieView.vue"),
    },
    {
      path: "/watch/episode/:id",
      name: "watch-episode",
      component: () => import("../views/WatchEpisodeView.vue"),
    },
    {
      path: "/select-profile",
      name: "select-profile",
      component: () => import("../views/SelectProfileView.vue"),
    },
    {
      path: "/forgot-password",
      name: "forgot-password",
      component: () => import("../views/PasswordResetRequestView.vue"),
    },
    {
      path: "/reset-password",
      name: "reset-password",
      component: () => import("../views/PasswordResetConfirmView.vue"),
    },
    {
      path: "/admin",
      component: () => import("../layouts/AdminLayout.vue"),
      children: [
        { path: "movies", name: "admin-movies", component: () => import("../views/admin/AdminMoviesView.vue") },
        { path: "movies/new", name: "admin-movie-new", component: () => import("../views/admin/AdminMovieEditView.vue") },
        { path: "movies/:slug", name: "admin-movie-edit", component: () => import("../views/admin/AdminMovieEditView.vue") },
        { path: "series", name: "admin-series", component: () => import("../views/admin/AdminSeriesView.vue") },
        { path: "series/new", name: "admin-series-new", component: () => import("../views/admin/AdminSeriesEditView.vue") },
        { path: "series/:slug", name: "admin-series-edit", component: () => import("../views/admin/AdminSeriesEditView.vue") },
        { path: "genres", name: "admin-genres", component: () => import("../views/admin/AdminGenresView.vue") },
        { path: "plans", name: "admin-plans", component: () => import("../views/admin/AdminPlansView.vue") },
      ],
    },
    {
      path: "/search",
      name: "search",
      component: () => import("../views/SearchView.vue"),
    },
  
  ],
});
