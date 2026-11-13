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
  ],
});
