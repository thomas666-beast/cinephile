<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { catalogApi } from "../api";
import type { MovieListItem } from "../api/types";
import PageHeader from "../components/PageHeader.vue";
import PosterTile from "../components/PosterTile.vue";
import LoadingLabel from "../components/LoadingLabel.vue";
import EmptyState from "../components/EmptyState.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const items = ref<MovieListItem[]>([]);
const count = ref(0);
const page = computed(() => Number(route.query.page ?? 1));
const loading = ref(true);
const error = ref<string | null>(null);
const PAGE_SIZE = 20;

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const data = await catalogApi.movies({ page: page.value });
    items.value = data.results;
    count.value = data.count;
  } catch {
    error.value = t("common.error");
  } finally {
    loading.value = false;
  }
}

function goToPage(p: number) {
  router.push({ query: { ...route.query, page: p === 1 ? undefined : p } });
}

onMounted(load);
watch(page, load);

const totalPages = computed(() => Math.max(1, Math.ceil(count.value / PAGE_SIZE)));
</script>

<template>
  <section class="max-w-6xl mx-auto px-6 py-16">
    <PageHeader
      :label="t('nav.movies')"
      :title="t('catalog.browseMovies')"
      :subtitle="t('catalog.browseMoviesSubtitle')"
    />

    <LoadingLabel v-if="loading" />
    <p v-else-if="error" class="text-blood-500">{{ error }}</p>

    <template v-else>
      <EmptyState v-if="items.length === 0" :message="t('catalog.noMovies')" />

      <ul
        v-else
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6"
      >
        <li v-for="m in items" :key="m.id">
          <PosterTile
            :to="{ name: 'movie-detail', params: { slug: m.slug } }"
            :title="m.title"
            :poster-url="m.poster"
            :meta="m.release_year ? String(m.release_year) : null"
          />
        </li>
      </ul>

      <nav
        v-if="totalPages > 1"
        class="mt-12 flex items-center justify-between label-caps"
      >
        <button
          type="button"
          class="frame px-4 py-2 disabled:opacity-30"
          :disabled="page <= 1"
          @click="goToPage(page - 1)"
        >
          {{ t("common.previous") }}
        </button>
        <span>{{ t("common.page", { n: page }) }}</span>
        <button
          type="button"
          class="frame px-4 py-2 disabled:opacity-30"
          :disabled="page >= totalPages"
          @click="goToPage(page + 1)"
        >
          {{ t("common.next") }}
        </button>
      </nav>
    </template>
  </section>
</template>
