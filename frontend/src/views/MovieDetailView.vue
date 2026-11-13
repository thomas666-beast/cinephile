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
      <!-- Backdrop as a strict rectangle, no overlay, title below -->
      <div class="frame">
        <div class="aspect-[16/9] bg-noir-800 overflow-hidden">
          <img
            v-if="movie.backdrop"
            :src="movie.backdrop"
            :alt="movie.title"
            class="w-full h-full object-cover"
          />
        </div>
      </div>

      <!-- Caption block: label, title, meta, action -->
      <div class="mt-8 grid md:grid-cols-[1fr_auto] gap-6 items-start">
        <div>
          <p class="label-caps mb-2">{{ t("nav.movies") }}</p>
          <h1 class="font-serif text-3xl md:text-5xl leading-[1.05] max-w-2xl">
            {{ movie.title }}
          </h1>
          <p v-if="metaLine.length" class="label-caps mt-4">
            {{ metaLine.join(" · ") }}
          </p>
          <div class="mt-4">
            <GenrePills :genres="movie.genres" />
          </div>
        </div>
        <button
          type="button"
          class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-5 py-2.5 transition-colors"
          :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
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
