<script setup lang="ts">
import { computed, onMounted, ref, watch, onBeforeUnmount } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { usePlayback } from "../composables/usePlayback";
import HlsPlayer from "../components/HlsPlayer.vue";
import { historyApi } from "../api";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const { state, fetchPlayback } = usePlayback();

const REFRESH_INTERVAL_MS = 25 * 60 * 1000;
let refreshTimer: ReturnType<typeof setTimeout> | null = null;

const slug = computed(() => String(route.params.slug));

async function load() {
  if (!auth.user) {
    router.push({ name: "sign-in", query: { next: route.fullPath } });
    return;
  }
  await fetchPlayback("movie", slug.value);
  if (state.value.kind === "unsubscribed") {
    router.push({ name: "plans" });
    return;
  }
  scheduleRefresh();
}

function scheduleRefresh() {
  if (refreshTimer) clearTimeout(refreshTimer);
  refreshTimer = setTimeout(async () => {
    if (state.value.kind !== "ready") return;
    await fetchPlayback("movie", slug.value);
    scheduleRefresh();
  }, REFRESH_INTERVAL_MS);
}

function retry() { load(); }

async function onProgress(data: { time: number; duration: number }) {
  if (!state.value || state.value.kind !== 'ready' || !state.value.data.content_id) return;
  
  try {
    await historyApi.save({
      content_type: "movie",
      content_id: state.value.data.content_id,
      progress_seconds: data.time,
      duration_seconds: data.duration,
    });
  } catch (e) {
    console.error("Failed to save progress", e);
  }
}

onMounted(load);
watch(slug, load);
onBeforeUnmount(() => { if (refreshTimer) clearTimeout(refreshTimer); });
</script>

<template>
  <section class="max-w-6xl mx-auto px-6 py-12">
    <RouterLink :to="`/movies/${slug}`" class="label-caps hover:text-paper-100">
      ← {{ t("player.backToCatalog") }}
    </RouterLink>

    <div class="mt-8 frame">
      <HlsPlayer
        v-if="state.kind === 'ready' && state.data.hls_manifest_url"
        :src="state.data.hls_manifest_url"
        autoplay
        @progress="onProgress"
      />
      <div v-else class="aspect-[16/9] flex items-center justify-center px-8 text-center">
        <p v-if="state.kind === 'loading' || state.kind === 'idle'" class="label-caps">
          {{ t("player.loading") }}
        </p>
        <p v-else-if="state.kind === 'processing'" class="label-caps">
          {{ t("player.processing") }}
        </p>
        <p v-else-if="state.kind === 'notfound'" class="label-caps">
          {{ t("player.notFound") }}
        </p>
        <div v-else-if="state.kind === 'error'" class="text-center">
          <p class="label-caps mb-4">{{ t("player.error") }}</p>
          <button
            type="button"
            class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-4 py-2"
            @click="retry"
          >
            {{ t("player.retry") }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
