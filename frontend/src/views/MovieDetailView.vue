<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { catalogApi } from "../api";
import type { MovieDetail } from "../api/types";
import LoadingLabel from "../components/LoadingLabel.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const movie = ref<MovieDetail | null>(null);
const loading = ref(true);
const notFound = ref(false);

async function load() {
  loading.value = true;
  notFound.value = false;
  try {
    movie.value = await catalogApi.movie(String(route.params.slug));
  } catch (e: any) {
    if (e?.response?.status === 404) notFound.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => route.params.slug, load);

const metaLine = computed(() => {
  if (!movie.value) return "";
  const parts: string[] = [];
  if (movie.value.release_year) parts.push(String(movie.value.release_year));
  if (movie.value.duration_minutes) parts.push(t("catalog.minutes", { n: movie.value.duration_minutes }));
  if (movie.value.genres.length) parts.push(movie.value.genres.map(g => g.name).join(", "));
  return parts.join("  ·  ");
});
</script>

<template>
  <div>
    <LoadingLabel v-if="loading" />
    <p v-else-if="notFound" class="label-caps text-center py-32">{{ t("common.notFound") }}</p>

    <article v-else-if="movie">
      <!-- HERO: full-width backdrop -->
      <section class="relative w-full" style="height: 70vh; min-height: 500px;">
        <div class="absolute inset-0 overflow-hidden">
          <img
            v-if="movie.backdrop"
            :src="movie.backdrop"
            :alt="movie.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-noir-800" />
          <div class="absolute inset-0 bg-gradient-to-t from-noir-950 via-noir-950/50 to-noir-950/10" />
        </div>

        <div class="relative h-full max-w-7xl mx-auto px-8 md:px-16 flex flex-col justify-end pb-20">
          <p class="label-caps mb-4">{{ t("nav.movies") }}</p>
          <h1 class="font-serif text-5xl md:text-7xl leading-[0.95] max-w-4xl mb-6">
            {{ movie.title }}
          </h1>
          <p v-if="metaLine" class="label-caps mb-8 text-paper-300">{{ metaLine }}</p>
          <div class="flex items-center gap-4">
            <button
              type="button"
              class="bg-paper-100 hover:bg-paper-300 text-noir-950 label-caps px-8 py-3 transition-colors"
              @click="router.push({ name: 'watch-movie', params: { slug: movie.slug } })"
            >
              {{ t("catalog.watch") }}
            </button>
            <button
              type="button"
              class="frame text-paper-100 label-caps px-6 py-3 hover:border-paper-100 transition-colors"
              @click="router.back()"
            >
              {{ t("common.back") }}
            </button>
          </div>
        </div>
      </section>

      <!-- Synopsis block below -->
      <section class="max-w-4xl mx-auto px-8 md:px-16 py-16">
        <p class="label-caps mb-4">Synopsis</p>
        <p class="text-paper-300 text-lg leading-relaxed whitespace-pre-line">
          {{ movie.synopsis || "—" }}
        </p>
      </section>
    </article>
  </div>
</template>
