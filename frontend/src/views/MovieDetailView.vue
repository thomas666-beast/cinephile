<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { catalogApi } from "../api";
import type { MovieDetail } from "../api/types";
import LoadingLabel from "../components/LoadingLabel.vue";
import GenrePills from "../components/GenrePills.vue";

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
  if (!movie.value) return [];
  const parts: string[] = [];
  if (movie.value.release_year) parts.push(String(movie.value.release_year));
  if (movie.value.duration_minutes) {
    parts.push(t("catalog.minutes", { n: movie.value.duration_minutes }));
  }
  return parts;
});
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

    <article v-else-if="movie">
      <!-- Hero -->
      <div class="relative frame overflow-hidden">
        <div class="aspect-[16/9] bg-noir-800">
          <img
            v-if="movie.backdrop"
            :src="movie.backdrop"
            :alt="movie.title"
            class="w-full h-full object-cover opacity-80"
          />
        </div>
        <div class="absolute inset-0 bg-gradient-to-t from-noir-950 via-noir-950/60 to-transparent" />
        <div class="absolute inset-x-0 bottom-0 p-8 md:p-12">
          <p class="label-caps mb-3">{{ t("nav.movies") }}</p>
          <h1 class="font-serif text-4xl md:text-6xl leading-[1.02] max-w-3xl">
            {{ movie.title }}
          </h1>
        </div>
      </div>

      <!-- Meta + action -->
      <div class="grid md:grid-cols-[1fr_auto] gap-6 items-start mt-8">
        <div>
          <p v-if="metaLine.length" class="label-caps mb-4">
            {{ metaLine.join(" · ") }}
          </p>
          <GenrePills :genres="movie.genres" />
        </div>
        <button
          type="button"
          class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-8 py-4"
          @click="router.push({ name: 'watch-movie', params: { slug: movie.slug } })"
        >
          {{ t("catalog.watch") }}
        </button>
      </div>

      <!-- Synopsis -->
      <div class="mt-12 max-w-2xl">
        <p class="label-caps mb-3">Synopsis</p>
        <p class="text-paper-300 leading-relaxed whitespace-pre-line">
          {{ movie.synopsis || "—" }}
        </p>
      </div>
    </article>
  </section>
</template>
