<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { catalogApi, historyApi } from "../api";
import type { MovieListItem, SeriesListItem, WatchProgressResponse } from "../api/types";
import PosterTile from "../components/PosterTile.vue";
import { useAuthStore } from "../stores/auth";

const { t } = useI18n();
const auth = useAuthStore();

const movies = ref<MovieListItem[]>([]);
const series = ref<SeriesListItem[]>([]);
const history = ref<WatchProgressResponse[]>([]);
const error = ref<string | null>(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const home = await catalogApi.home();
    movies.value = home.latest_movies;
    series.value = home.latest_series;
    
    if (auth.user) {
      history.value = await historyApi.list();
    }
  } catch (e) {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
});

function formatYears(s: SeriesListItem): string | null {
  if (!s.start_year && !s.end_year) return null;
  if (s.start_year && !s.end_year) return t("catalog.fromYear", { year: s.start_year });
  if (s.start_year && s.end_year && s.start_year !== s.end_year) {
    return t("catalog.toYear", { start: s.start_year, end: s.end_year });
  }
  return String(s.start_year);
}

function resumeLink(item: WatchProgressResponse) {
  if (item.content_type === "movie") {
    return { name: "watch-movie", params: { slug: item.slug } };
  }
  return { name: "watch-episode", params: { id: item.content_id } };
}
</script>

<template>
  <section class="max-w-6xl mx-auto px-6 py-16">
    <!-- Hero -->
    <div class="frame p-12 mb-16">
      <p class="label-caps mb-4">A cinema in your browser</p>
      <h1 class="text-5xl md:text-6xl leading-[1.05] max-w-3xl">
        {{ t("home.heroTitle") }}
      </h1>
      <p class="mt-6 text-paper-300 max-w-xl">
        {{ t("home.heroSubtitle") }}
      </p>
    </div>

    <!-- Continue Watching -->
    <section v-if="history.length > 0" class="mb-16">
      <div class="flex items-baseline justify-between mb-6">
        <h2 class="text-2xl">{{ t("home.continueWatching") }}</h2>
      </div>
      <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
        <li v-for="item in history" :key="item.id">
          <RouterLink :to="resumeLink(item)" class="block frame group transition-colors">
            <div class="aspect-[2/3] bg-noir-800 overflow-hidden relative">
              <img v-if="item.poster" :src="item.poster" :alt="item.title" class="w-full h-full object-cover" />
              <!-- Progress Bar (Hitchcock red accent) -->
              <div class="absolute bottom-0 left-0 w-full h-1 bg-noir-950/80">
                <div class="h-full bg-blood-500" :style="{ width: item.percent + '%' }"></div>
              </div>
            </div>
            <div class="p-3 border-t border-paper-300/20">
              <p class="font-serif text-base leading-tight line-clamp-1">{{ item.title }}</p>
            </div>
          </RouterLink>
        </li>
      </ul>
    </section>

    <!-- Loading / error -->
    <p v-if="loading" class="label-caps">{{ t("common.loading") }}</p>
    <p v-else-if="error" class="text-blood-500">{{ error }}</p>

    <!-- Content -->
    <template v-else>
      <section class="mb-16">
        <div class="flex items-baseline justify-between mb-6">
          <h2 class="text-2xl">{{ t("home.latestMovies") }}</h2>
        </div>
        <div v-if="movies.length === 0" class="label-caps">
          {{ t("home.emptyCatalog") }}
        </div>
        <ul v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
          <li v-for="m in movies" :key="m.id">
            <PosterTile
              :to="{ name: 'movie-detail', params: { slug: m.slug } }"
              :title="m.title"
              :poster-url="m.poster"
              :meta="m.release_year ? String(m.release_year) : null"
            />
          </li>
        </ul>
      </section>

      <section>
        <div class="flex items-baseline justify-between mb-6">
          <h2 class="text-2xl">{{ t("home.latestSeries") }}</h2>
        </div>
        <div v-if="series.length === 0" class="label-caps">
          {{ t("home.emptyCatalog") }}
        </div>
        <ul v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
          <li v-for="s in series" :key="s.id">
            <PosterTile
              :to="{ name: 'series-detail', params: { slug: s.slug } }"
              :title="s.title"
              :poster-url="s.poster"
              :meta="formatYears(s)"
            />
          </li>
        </ul>
      </section>
    </template>
  </section>
</template>
