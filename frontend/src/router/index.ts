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
  ],
});
