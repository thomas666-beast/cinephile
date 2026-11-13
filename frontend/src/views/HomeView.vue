<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { catalogApi, historyApi } from "../api";
import type { MovieListItem, SeriesListItem, WatchProgressResponse, MovieDetail } from "../api/types";
import PosterTile from "../components/PosterTile.vue";
import { useAuthStore } from "../stores/auth";
import { useProfileStore } from "../stores/profiles";

const { t } = useI18n();
const auth = useAuthStore();
const profiles = useProfileStore();
const router = useRouter();

const movies = ref<MovieListItem[]>([]);
const series = ref<SeriesListItem[]>([]);
const history = ref<WatchProgressResponse[]>([]);
const heroMovie = ref<MovieDetail | null>(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const home = await catalogApi.home();
    movies.value = home.latest_movies;
    series.value = home.latest_series;
    if (movies.value.length > 0) {
      heroMovie.value = await catalogApi.movie(movies.value[0].slug);
    }
    if (auth.user && profiles.activeId) {
      history.value = await historyApi.list(profiles.activeId);
    }
  } finally {
    loading.value = false;
  }
});

const heroMeta = computed(() => {
  if (!heroMovie.value) return "";
  const parts: string[] = [];
  if (heroMovie.value.release_year) parts.push(String(heroMovie.value.release_year));
  if (heroMovie.value.duration_minutes) parts.push(`${heroMovie.value.duration_minutes} min`);
  if (heroMovie.value.genres.length) parts.push(heroMovie.value.genres.map(g => g.name).join(", "));
  return parts.join("  ·  ");
});

function resumeLink(item: WatchProgressResponse) {
  if (item.content_type === "movie") return { name: "watch-movie", params: { slug: item.slug } };
  return { name: "watch-episode", params: { id: item.content_id } };
}

function formatYears(s: SeriesListItem): string | null {
  if (s.start_year && s.end_year && s.start_year !== s.end_year) return `${s.start_year}–${s.end_year}`;
  return s.start_year ? String(s.start_year) : null;
}
</script>

<template>
  <div>
    <p v-if="loading" class="label-caps text-center py-32">{{ t("common.loading") }}</p>

    <template v-else>
      <!-- HERO: full-width, cinematic -->
      <section v-if="heroMovie" class="relative w-full" style="height: 80vh; min-height: 600px;">
        <!-- Backdrop -->
        <div class="absolute inset-0 overflow-hidden">
          <img
            v-if="heroMovie.backdrop"
            :src="heroMovie.backdrop"
            :alt="heroMovie.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-noir-800" />
          <!-- Gradient: bottom-heavy into noir so text is legible -->
          <div class="absolute inset-0 bg-gradient-to-t from-noir-950 via-noir-950/60 to-noir-950/20" />
        </div>

        <!-- Content anchored to left, well away from edges -->
        <div class="relative h-full max-w-7xl mx-auto px-8 md:px-16 flex flex-col justify-end pb-24">
          <p class="label-caps mb-4">{{ t("nav.movies") }}</p>
          <h1 class="font-serif text-5xl md:text-7xl lg:text-8xl leading-[0.95] max-w-4xl mb-6">
            {{ heroMovie.title }}
          </h1>
          <p v-if="heroMeta" class="label-caps mb-6 text-paper-300">{{ heroMeta }}</p>
          <p class="text-paper-100/80 max-w-xl mb-8 leading-relaxed">
            {{ heroMovie.synopsis || "" }}
          </p>
          <div class="flex items-center gap-4">
            <button
              type="button"
              class="bg-paper-100 hover:bg-paper-300 text-noir-950 label-caps px-6 py-3 transition-colors"
              @click="router.push({ name: 'watch-movie', params: { slug: heroMovie.slug } })"
            >
              {{ t("catalog.watch") }}
            </button>
            <button
              type="button"
              class="frame text-paper-100 label-caps px-6 py-3 hover:border-paper-100 transition-colors"
              @click="router.push({ name: 'movie-detail', params: { slug: heroMovie.slug } })"
            >
              {{ t("catalog.moreInfo") }}
            </button>
          </div>
        </div>
      </section>

      <!-- CONTINUE WATCHING (only if logged in with history) -->
      <section v-if="history.length > 0" class="max-w-7xl mx-auto px-8 md:px-16 -mt-8 relative z-10">
        <p class="label-caps mb-4">{{ t("home.continueWatching") }}</p>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          <RouterLink
            v-for="item in history"
            :key="item.id"
            :to="resumeLink(item)"
            class="block group"
          >
            <div class="relative aspect-[2/3] bg-noir-800 overflow-hidden">
              <img
                v-if="item.poster"
                :src="item.poster"
                :alt="item.title"
                class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
              />
              <!-- Progress bar: bottom, blood-red -->
              <div class="absolute inset-x-0 bottom-0 h-1 bg-noir-950/80">
                <div class="h-full bg-blood-500" :style="{ width: item.percent + '%' }" />
              </div>
            </div>
            <p class="font-serif text-base mt-2 leading-tight line-clamp-1">{{ item.title }}</p>
          </RouterLink>
        </div>
      </section>

      <!-- LATEST MOVIES -->
      <section class="max-w-7xl mx-auto px-8 md:px-16 mt-20">
        <div class="flex items-baseline justify-between mb-6">
          <h2 class="font-serif text-3xl">{{ t("home.latestMovies") }}</h2>
          <RouterLink to="/movies" class="label-caps text-paper-300 hover:text-paper-100">
            {{ t("common.viewAll") }} →
          </RouterLink>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          <PosterTile
            v-for="m in movies.slice(0, 10)"
            :key="m.id"
            :to="{ name: 'movie-detail', params: { slug: m.slug } }"
            :title="m.title"
            :poster-url="m.poster"
            :meta="m.release_year ? String(m.release_year) : null"
          />
        </div>
      </section>

      <!-- LATEST SERIES -->
      <section class="max-w-7xl mx-auto px-8 md:px-16 mt-20 pb-24">
        <div class="flex items-baseline justify-between mb-6">
          <h2 class="font-serif text-3xl">{{ t("home.latestSeries") }}</h2>
          <RouterLink to="/series" class="label-caps text-paper-300 hover:text-paper-100">
            {{ t("common.viewAll") }} →
          </RouterLink>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          <PosterTile
            v-for="s in series.slice(0, 10)"
            :key="s.id"
            :to="{ name: 'series-detail', params: { slug: s.slug } }"
            :title="s.title"
            :poster-url="s.poster"
            :meta="formatYears(s)"
          />
        </div>
      </section>
    </template>
  </div>
</template>
