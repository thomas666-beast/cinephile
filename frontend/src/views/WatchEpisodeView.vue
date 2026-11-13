<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { usePlayback } from "../composables/usePlayback";
import HlsPlayer from "../components/HlsPlayer.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const { state, fetchPlayback } = usePlayback();

const REFRESH_INTERVAL_MS = 25 * 60 * 1000;
let refreshTimer: ReturnType<typeof setTimeout> | null = null;

const episodeId = computed(() => Number(route.params.id));

async function load() {
  if (!auth.user) {
    router.push({ name: "sign-in", query: { next: route.fullPath } });
    return;
  }
  await fetchPlayback("episode", episodeId.value);
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
    await fetchPlayback("episode", episodeId.value);
    scheduleRefresh();
  }, REFRESH_INTERVAL_MS);
}

onMounted(load);
watch(episodeId, load);
</script>

<template>
  <section class="max-w-6xl mx-auto px-6 py-12">
    <RouterLink to="/series" class="label-caps hover:text-paper-100">
      ← {{ t("player.backToCatalog") }}
    </RouterLink>

    <div class="mt-8 frame">
      <HlsPlayer
        v-if="state.kind === 'ready' && state.data.hls_manifest_url"
        :src="state.data.hls_manifest_url"
        autoplay
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
      </div>
    </div>
  </section>
</template>
