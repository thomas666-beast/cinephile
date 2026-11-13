<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import Hls from "hls.js";

const props = defineProps<{
  src: string;
  posterUrl?: string | null;
  autoplay?: boolean;
}>();

const emit = defineEmits<{
  (e: "ended"): void;
  (e: "error", msg: string): void;
  (e: "progress", data: { time: number; duration: number }): void; // <-- ADD THIS
}>();

const { t } = useI18n();
const videoRef = ref<HTMLVideoElement | null>(null);
const hlsRef = ref<Hls | null>(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const isReady = ref(false);
const hasError = ref(false);

function attach(src: string) {
  const video = videoRef.value;
  if (!video) return;

  // Tear down any previous instance
  if (hlsRef.value) {
    hlsRef.value.destroy();
    hlsRef.value = null;
  }

  if (Hls.isSupported()) {
    const hls = new Hls({ enableWorker: true, lowLatencyMode: false });
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      isReady.value = true;
      if (props.autoplay) video.play().catch(() => {});
    });
    hls.on(Hls.Events.ERROR, (_event, data) => {
      // NETWORK errors are recoverable via retry; MEDIA errors typically need re-fetch
      if (data.fatal) {
        if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
          hls.startLoad();
        } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
          hls.recoverMediaError();
        } else {
          hasError.value = true;
          emit("error", data.details);
        }
      }
    });
    hls.loadSource(src);
    hls.attachMedia(video);
    hlsRef.value = hls;
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    // Native HLS (Safari, iOS)
    video.src = src;
    isReady.value = true;
    if (props.autoplay) video.play().catch(() => {});
  } else {
    hasError.value = true;
    emit("error", "HLS not supported");
  }
}

function onLoadedMetadata() {
  const video = videoRef.value;
  if (!video) return;
  duration.value = Number.isFinite(video.duration) ? video.duration : 0;
}

let lastEmit = 0;
function onTimeUpdate() {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime;
    
    // Emit progress every 10 seconds
    const now = Date.now();
    if (now - lastEmit > 10000) {
      emit("progress", { 
        time: videoRef.value.currentTime, 
        duration: videoRef.value.duration 
      });
      lastEmit = now;
    }
  }
}

function togglePlay() {
  const v = videoRef.value;
  if (!v) return;
  if (v.paused) v.play().catch(() => {});
  else v.pause();
}

function onPlay() { isPlaying.value = true; }
function onPause() { isPlaying.value = false; }
function onEnded() { emit("ended"); }

function onScrub(e: Event) {
  const v = videoRef.value;
  if (!v) return;
  const input = e.target as HTMLInputElement;
  v.currentTime = Number(input.value);
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return "00:00";
  const s = Math.floor(seconds % 60);
  const m = Math.floor((seconds / 60) % 60);
  const h = Math.floor(seconds / 3600);
  const mm = String(m).padStart(2, "0");
  const ss = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

// Allow parent to swap src (e.g., token refresh) without recreating the component
watch(() => props.src, (next, prev) => {
  if (next && next !== prev) {
    // Preserve current time when reattaching
    const resumeAt = videoRef.value?.currentTime ?? 0;
    attach(next);
    if (videoRef.value && resumeAt > 0) {
      videoRef.value.addEventListener("loadedmetadata", () => {
        if (videoRef.value) videoRef.value.currentTime = resumeAt;
      }, { once: true });
    }
  }
});

onMounted(() => {
  if (props.src) attach(props.src);
});

onBeforeUnmount(() => {
  hlsRef.value?.destroy();
  hlsRef.value = null;
});
</script>

<template>
  <div class="relative w-full bg-black" style="aspect-ratio: 16/9;">
    <video
      ref="videoRef"
      class="w-full h-full"
      :poster="posterUrl ?? undefined"
      playsinline
      @loadedmetadata="onLoadedMetadata"
      @timeupdate="onTimeUpdate"
      @play="onPlay"
      @pause="onPause"
      @ended="onEnded"
      @click="togglePlay"
    />

    <p v-if="!isReady && !hasError" class="absolute inset-0 flex items-center justify-center label-caps">
      {{ t("player.loading") }}
    </p>

    <!-- Controls strip: shown after ready, hairline, no fill -->
    <div
      v-if="isReady && !hasError"
      class="absolute inset-x-0 bottom-0 px-6 pb-4 pt-12 bg-gradient-to-t from-black/80 to-transparent"
    >
      <input
        type="range"
        min="0"
        :max="duration"
        step="0.1"
        :value="currentTime"
        class="w-full h-px bg-paper-300/40 accent-blood-500 cursor-pointer"
        @input="onScrub"
        :aria-label="t('player.play')"
      />
      <div class="flex items-center justify-between mt-3 label-caps">
        <div class="flex items-center gap-4">
          <button type="button" @click="togglePlay" class="hover:text-blood-500">
            {{ isPlaying ? t("player.pause") : t("player.play") }}
          </button>
          <span>{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
