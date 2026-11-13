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
  (e: "progress", data: { time: number; duration: number }): void;
}>();

const { t } = useI18n();
const videoRef = ref<HTMLVideoElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);
const hlsRef = ref<Hls | null>(null);

const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const isReady = ref(false);
const hasError = ref(false);
const volume = ref(1);
const isMuted = ref(false);
const isFullscreen = ref(false);

let lastEmit = 0;

function attach(src: string) {
  const video = videoRef.value;
  if (!video) return;

  if (hlsRef.value) {
    hlsRef.value.destroy();
    hlsRef.value = null;
  }

  if (Hls.isSupported()) {
    const hls = new Hls({ enableWorker: true });
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      isReady.value = true;
      if (props.autoplay) video.play().catch(() => {});
    });
    hls.on(Hls.Events.ERROR, (_e, data) => {
      if (data.fatal) {
        if (data.type === Hls.ErrorTypes.NETWORK_ERROR) hls.startLoad();
        else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) hls.recoverMediaError();
        else {
          hasError.value = true;
          emit("error", data.details);
        }
      }
    });
    hls.loadSource(src);
    hls.attachMedia(video);
    hlsRef.value = hls;
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = src;
    isReady.value = true;
    if (props.autoplay) video.play().catch(() => {});
  } else {
    hasError.value = true;
    emit("error", "HLS not supported");
  }
}

function togglePlay() {
  const v = videoRef.value;
  if (!v) return;
  if (v.paused) v.play().catch(() => {});
  else v.pause();
}

function onLoadedMetadata() {
  if (videoRef.value) duration.value = videoRef.value.duration;
}

function onTimeUpdate() {
  const v = videoRef.value;
  if (!v) return;
  currentTime.value = v.currentTime;
  
  const now = Date.now();
  if (now - lastEmit > 10000) {
    emit("progress", { time: v.currentTime, duration: v.duration });
    lastEmit = now;
  }
}

function onScrub(e: Event) {
  const v = videoRef.value;
  if (!v) return;
  v.currentTime = Number((e.target as HTMLInputElement).value);
}

function onVolumeChange(e: Event) {
  const v = videoRef.value;
  if (!v) return;
  const val = Number((e.target as HTMLInputElement).value);
  v.volume = val;
  volume.value = val;
  isMuted.value = val === 0;
}

function toggleMute() {
  const v = videoRef.value;
  if (!v) return;
  v.muted = !v.muted;
  isMuted.value = v.muted;
  if (!v.muted && v.volume === 0) {
    v.volume = 0.5;
    volume.value = 0.5;
  }
}

function toggleFullscreen() {
  const el = containerRef.value;
  if (!el) return;
  if (!document.fullscreenElement) {
    el.requestFullscreen().catch(() => {});
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
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

watch(() => props.src, (next, prev) => {
  if (next && next !== prev) {
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
  <div ref="containerRef" class="relative w-full bg-black aspect-video group overflow-hidden">
    <video
      ref="videoRef"
      class="w-full h-full object-contain"
      :poster="posterUrl ?? undefined"
      playsinline
      @loadedmetadata="onLoadedMetadata"
      @timeupdate="onTimeUpdate"
      @play="isPlaying = true"
      @pause="isPlaying = false"
      @ended="emit('ended')"
      @click="togglePlay"
    />

    <p v-if="!isReady && !hasError" class="absolute inset-0 flex items-center justify-center label-caps">
      {{ t("player.loading") }}
    </p>

    <!-- Custom Controls -->
    <div
      v-if="isReady && !hasError"
      class="absolute inset-x-0 bottom-0 px-4 pb-4 pt-16 bg-gradient-to-t from-black/90 via-black/40 to-transparent transition-opacity duration-300"
      :class="isPlaying ? 'opacity-0 group-hover:opacity-100' : 'opacity-100'"
    >
      <!-- Scrubber -->
      <input
        type="range"
        min="0"
        :max="duration"
        step="0.1"
        :value="currentTime"
        class="w-full h-1 bg-paper-300/30 accent-blood-500 cursor-pointer appearance-none rounded-none focus:outline-none"
        @input="onScrub"
      />

      <!-- Bottom bar -->
      <div class="flex items-center justify-between mt-3">
        <div class="flex items-center gap-4">
          <!-- Play/Pause -->
          <button type="button" class="text-paper-100 hover:text-blood-500 transition-colors" @click="togglePlay">
            <svg v-if="!isPlaying" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          </button>

          <!-- Volume -->
          <div class="flex items-center gap-2 group/volume relative">
            <button type="button" class="text-paper-100 hover:text-blood-500 transition-colors" @click="toggleMute">
              <svg v-if="isMuted || volume === 0" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
            </button>
            <!-- Volume Slider (shows on hover) -->
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              :value="volume"
              class="w-0 group-hover/volume:w-20 transition-all duration-300 h-1 bg-paper-300/30 accent-blood-500 cursor-pointer appearance-none rounded-none focus:outline-none"
              @input="onVolumeChange"
            />
          </div>

          <!-- Time -->
          <span class="label-caps text-xs">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </span>
        </div>

        <!-- Fullscreen -->
        <button type="button" class="text-paper-100 hover:text-blood-500 transition-colors" @click="toggleFullscreen">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>
