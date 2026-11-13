<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { catalogApi } from "../api";
import type { SearchResponse } from "../api/types";
import PageHeader from "../components/PageHeader.vue";
import PosterTile from "../components/PosterTile.vue";
import LoadingLabel from "../components/LoadingLabel.vue";
import EmptyState from "../components/EmptyState.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const query = computed(() => String(route.query.q ?? "").trim());
const type = computed<"all" | "movie" | "series">(() => {
  const t = route.query.type;
  if (t === "movie" || t === "series") return t;
  return "all";
});

const data = ref<SearchResponse | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

async function load() {
  if (!query.value) {
    data.value = { query: "", type: type.value, movies: { count: 0, results: [] }, series: { count: 0, results: [] } };
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    data.value = await catalogApi.search(query.value, type.value);
  } catch (e) {
    console.error("Search error:", e);
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

function setType(next: "all" | "movie" | "series") {
  router.push({ name: "search", query: { ...route.query, type: next === "all" ? undefined : next } });
}

onMounted(load);
watch([query, type], load);
</script>

<template>
  <section class="max-w-6xl mx-auto px-6 py-16">
    <PageHeader
      :label="t('nav.search')"
      :title="query ? t('search.resultsFor', { query }) : t('nav.search')"
    />

    <!-- Filter tabs -->
    <nav v-if="query" class="flex items-center gap-2 mb-10">
      <button
        v-for="opt in [
          { value: 'all', label: t('search.filterAll') },
          { value: 'movie', label: t('search.filterMovies') },
          { value: 'series', label: t('search.filterSeries') },
        ]"
        :key="opt.value"
        type="button"
        class="label-caps px-4 py-1.5 border transition-colors"
        :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
        :class="type === opt.value
          ? 'bg-paper-100 !text-noir-950 border-paper-100'
          : 'text-paper-300 border-paper-300/30 hover:border-paper-100 hover:text-paper-100'"
        @click="setType(opt.value as any)"
      >
        {{ opt.label }}
      </button>
    </nav>

    <LoadingLabel v-if="loading" />
    <p v-else-if="error" class="text-blood-500">{{ error }}</p>

    <EmptyState v-else-if="!query" :message="t('search.noQuery')" />

    <template v-else-if="data">
      <EmptyState
        v-if="data.movies.count === 0 && data.series.count === 0"
        :message="t('search.noResults', { query })"
      />

      <template v-else>
        <!-- Movies -->
        <section v-if="data.movies.count > 0" class="mb-16">
          <p class="label-caps mb-4">
            {{ t('search.filterMovies') }} — {{ t('search.moviesCount', { n: data.movies.count }) }}
          </p>
          <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
            <li v-for="m in data.movies.results" :key="m.id">
              <PosterTile
                :to="{ name: 'movie-detail', params: { slug: m.slug } }"
                :title="m.title"
                :poster-url="m.poster"
                :meta="m.release_year ? String(m.release_year) : null"
              />
            </li>
          </ul>
        </section>

        <!-- Series -->
        <section v-if="data.series.count > 0">
          <p class="label-caps mb-4">
            {{ t('search.filterSeries') }} — {{ t('search.seriesCount', { n: data.series.count }) }}
          </p>
          <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
            <li v-for="s in data.series.results" :key="s.id">
              <PosterTile
                :to="{ name: 'series-detail', params: { slug: s.slug } }"
                :title="s.title"
                :poster-url="s.poster"
                :meta="s.start_year ? String(s.start_year) : null"
              />
            </li>
          </ul>
        </section>
      </template>
    </template>
  </section>
</template>
