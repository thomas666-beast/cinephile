import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/HomeView.vue"),
    },
    // Filled in by Tasks 15-19:
    // { path: "/movies", name: "movies", ... }
    // { path: "/movies/:slug", name: "movie-detail", ... }
    // { path: "/series/:slug", name: "series-detail", ... }
    // { path: "/sign-in", name: "sign-in", ... }
    // { path: "/register", name: "register", ... }
    // { path: "/plans", name: "plans", ... }
    // { path: "/watch/movie/:slug", name: "watch-movie", ... }
  ],
});
