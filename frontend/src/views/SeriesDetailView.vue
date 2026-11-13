<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { catalogApi } from "../api";
import type { SeriesDetail, SeasonItem, EpisodeItem } from "../api/types";
import LoadingLabel from "../components/LoadingLabel.vue";
import GenrePills from "../components/GenrePills.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const series = ref<SeriesDetail | null>(null);
const loading = ref(true);
const notFound = ref(false);
const activeSeason = ref<number | null>(null);

async function load() {
  loading.value = true;
  notFound.value = false;
  try {
    series.value = await catalogApi.series(String(route.params.slug));
    // Open the first season by default
    if (series.value.seasons.length > 0 && activeSeason.value === null) {
      activeSeason.value = series.value.seasons[0].id;
    }
  } catch (e: any) {
    if (e?.response?.status === 404) notFound.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => route.params.slug, () => {
  activeSeason.value = null;
  load();
});

const currentSeason = computed<SeasonItem | null>(() => {
  if (!series.value || activeSeason.value === null) return null;
  return series.value.seasons.find(s => s.id === activeSeason.value) ?? null;
});

const yearMeta = computed(() => {
  if (!series.value) return null;
  const { start_year, end_year } = series.value;
  if (start_year && end_year && start_year !== end_year) return `${start_year}–${end_year}`;
  return start_year ? String(start_year) : null;
});

function episodeCountLabel(n: number): string {
  return n === 1 ? t("catalog.episodeCountOne") : t("catalog.episodeCount", { n });
}

function playEpisode(ep: EpisodeItem) {
  router.push({ name: "watch-episode", params: { id: String(ep.id) } });
}
</script>

<template>
  <section class="max-w-6xl mx-auto px-6 py-16">
    <button
      type="button"
      class="label-caps mb-8 hover:text-paper-100"
      @click="router.back()"
    >
      ← {{ t("common.back") }}
    </button>

    <LoadingLabel v-if="loading" />
    <p v-else-if="notFound" class="label-caps">{{ t("common.notFound") }}</p>

    <article v-else-if="series">
      <!-- Hero -->
      <div class="relative frame overflow-hidden">
        <div class="aspect-[16/9] bg-noir-800">
          <img
            v-if="series.backdrop"
            :src="series.backdrop"
            :alt="series.title"
            class="w-full h-full object-cover opacity-80"
          />
        </div>
        <div class="absolute inset-0 bg-gradient-to-t from-noir-950 via-noir-950/60 to-transparent" />
        <div class="absolute inset-x-0 bottom-0 p-8 md:p-12">
          <p class="label-caps mb-3">{{ t("nav.series") }}</p>
          <h1 class="font-serif text-4xl md:text-6xl leading-[1.02] max-w-3xl">
            {{ series.title }}
          </h1>
        </div>
      </div>

      <!-- Meta -->
      <div class="mt-8">
        <p v-if="yearMeta" class="label-caps mb-4">{{ yearMeta }}</p>
        <GenrePills :genres="series.genres" />
      </div>

      <!-- Synopsis -->
      <div v-if="series.synopsis" class="mt-12 max-w-2xl">
        <p class="label-caps mb-3">Synopsis</p>
        <p class="text-paper-300 leading-relaxed whitespace-pre-line">
          {{ series.synopsis }}
        </p>
      </div>

      <!-- Seasons -->
      <section v-if="series.seasons.length" class="mt-16">
        <p class="label-caps mb-4">{{ t("catalog.seasons") }}</p>

        <nav class="flex flex-wrap gap-2 mb-8">
          <button
            v-for="s in series.seasons"
            :key="s.id"
            type="button"
            class="label-caps px-4 py-2 border border-paper-300/30"
            :class="activeSeason === s.id
              ? 'bg-paper-100 text-noir-950 border-paper-100'
              : 'hover:border-paper-100'"
            @click="activeSeason = s.id"
          >
            {{ t("catalog.season", { n: s.number }) }}
          </button>
        </nav>

        <div v-if="currentSeason">
          <div class="flex items-baseline justify-between mb-4 pb-3 border-b border-paper-300/20">
            <h2 class="font-serif text-2xl">{{ currentSeason.title || t("catalog.season", { n: currentSeason.number }) }}</h2>
            <p class="label-caps">{{ episodeCountLabel(currentSeason.episodes.length) }}</p>
          </div>

          <EmptyState v-if="currentSeason.episodes.length === 0" :message="t('catalog.noEpisodes')" />

          <ul v-else class="divide-y divide-paper-300/15">
            <li
              v-for="ep in currentSeason.episodes"
              :key="ep.id"
              class="grid grid-cols-[auto_1fr_auto_auto] gap-4 items-center py-4 hover:bg-noir-900 transition-colors"
              :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
            >
              <span class="label-caps w-10">
                {{ String(ep.number).padStart(2, "0") }}
              </span>
              <div>
                <p class="font-serif text-lg leading-tight">{{ ep.title }}</p>
                <p v-if="ep.air_date" class="label-caps mt-1">{{ ep.air_date }}</p>
              </div>
              <span v-if="ep.duration_minutes" class="label-caps">
                {{ t("catalog.minutes", { n: ep.duration_minutes }) }}
              </span>
              <button
                type="button"
                class="label-caps hover:text-blood-500"
                @click="playEpisode(ep)"
              >
                {{ t("catalog.watch") }}
              </button>
            </li>
          </ul>
        </div>
      </section>

      <EmptyState v-else :message="t('catalog.noEpisodes')" />
    </article>
  </section>
</template>
