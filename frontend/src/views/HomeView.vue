<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { catalogApi } from "../api";
import type { MovieListItem, SeriesListItem } from "../api/types";

const { t } = useI18n();

const movies = ref<MovieListItem[]>([]);
const series = ref<SeriesListItem[]>([]);
const error = ref<string | null>(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const home = await catalogApi.home();
    movies.value = home.latest_movies;
    series.value = home.latest_series;
  } catch (e) {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
});
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
        <ul v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          <li v-for="m in movies" :key="m.id" class="frame">
            <div class="aspect-[2/3] bg-noir-800"></div>
            <div class="p-3">
              <p class="font-serif text-lg leading-tight">{{ m.title }}</p>
              <p class="label-caps mt-1">{{ m.release_year }}</p>
            </div>
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
        <ul v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          <li v-for="s in series" :key="s.id" class="frame">
            <div class="aspect-[2/3] bg-noir-800"></div>
            <div class="p-3">
              <p class="font-serif text-lg leading-tight">{{ s.title }}</p>
              <p class="label-caps mt-1">{{ s.start_year }}</p>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </section>
</template>
