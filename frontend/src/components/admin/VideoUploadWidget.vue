<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { adminApi } from "../../api";
import AdminPrimaryButton from "./AdminPrimaryButton.vue";

type Status = "idle" | "uploading" | "processing" | "ready" | "failed";

const props = defineProps<{
  movieId: number;
  currentStatus: "pending" | "uploaded" | "processing" | "ready" | "failed" | null;
  currentError: string | null;
}>();

const emit = defineEmits<{ (e: "updated"): void }>();

const { t } = useI18n();
const status = ref<Status>("idle");
const progress = ref(0);
const errorMessage = ref<string | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

let pollTimer: ReturnType<typeof setInterval> | null = null;
const trackedAssetId = ref<number | null>(null);

function stopPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = null;
}

function startPolling() {
  stopPolling();
  if (!trackedAssetId.value) return;
  pollTimer = setInterval(async () => {
    try {
      const data = await adminApi.getMovie(props.movieId.toString());
      if (data.video_status && data.video_status.id === trackedAssetId.value) {
        if (data.video_status.status === "ready") {
          status.value = "ready";
          stopPolling();
          emit("updated");
        } else if (data.video_status.status === "failed") {
          status.value = "failed";
          errorMessage.value = data.video_status.processing_error ?? "Unknown error";
          stopPolling();
          emit("updated");
        } else {
          status.value = "processing";
        }
      }
    } catch {
      // ignore
    }
  }, 3000);
}

watch(
  () => props.currentStatus,
  (next) => {
    if (next === "ready") status.value = "ready";
    else if (next === "processing") { status.value = "processing"; startPolling(); }
    else if (next === "failed") { status.value = "failed"; errorMessage.value = props.currentError; }
    else if (next === "uploaded") { status.value = "processing"; startPolling(); }
  },
  { immediate: true },
);

function pickFile() { fileInput.value?.click(); }

async function onFileSelected(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;

  status.value = "uploading";
  progress.value = 0;
  errorMessage.value = null;

  try {
    const asset = await adminApi.uploadVideo(
      props.movieId, file, file.type || "video/mp4",
      (pct) => { progress.value = pct; },
    );
    trackedAssetId.value = asset.id;
    status.value = "processing";
    startPolling();
    emit("updated");
  } catch (e: any) {
    status.value = "failed";
    errorMessage.value = e?.response?.data?.detail ?? "Upload failed";
  } finally {
    if (fileInput.value) fileInput.value.value = "";
  }
}

const statusLabel = computed(() => {
  switch (status.value) {
    case "idle": return t("admin.statusNoVideo");
    case "uploading": return `${t("admin.processing")} ${progress.value}%`;
    case "processing": return t("admin.processing");
    case "ready": return t("admin.ready");
    case "failed": return t("admin.failed");
  }
});

onBeforeUnmount(stopPolling);
</script>

<template>
  <div class="frame p-5">
    <p class="label-caps mb-2">Video</p>
    <p class="font-serif text-base mb-4">{{ statusLabel }}</p>

    <div v-if="status === 'uploading'" class="mb-3">
      <div class="w-full h-px bg-paper-300/30 relative">
        <div class="absolute left-0 top-0 h-full bg-blood-500" :style="{ width: progress + '%' }" />
      </div>
    </div>

    <p v-if="status === 'failed' && errorMessage" class="text-xs text-blood-500 mb-3 break-words">
      {{ errorMessage }}
    </p>

    <AdminPrimaryButton
      :disabled="status === 'uploading' || status === 'processing'"
      @click="pickFile"
    >
      {{ status === 'ready' ? "Replace video" : "Upload video" }}
    </AdminPrimaryButton>

    <input ref="fileInput" type="file" accept="video/*" class="hidden" @change="onFileSelected" />
  </div>
</template>
