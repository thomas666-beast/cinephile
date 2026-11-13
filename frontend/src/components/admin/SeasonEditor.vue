<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { adminApi } from "../../api";
import AdminPrimaryButton from "./AdminPrimaryButton.vue";
import AdminSecondaryButton from "./AdminSecondaryButton.vue";

const props = defineProps<{
  seriesId: number;
  season: { id: number; number: number; title: string; episodes: any[] };
}>();

const emit = defineEmits<{ (e: "changed"): void }>();
const { t } = useI18n();

const newEpisodeTitle = ref("");

async function addEpisode() {
  if (!newEpisodeTitle.value.trim()) return;
  const nextNumber = (props.season.episodes.at(-1)?.number ?? 0) + 1;
  await adminApi.createEpisode({
    season: props.season.id,
    number: nextNumber,
    title: newEpisodeTitle.value.trim(),
    status: "draft",
  });
  newEpisodeTitle.value = "";
  emit("changed");
}

async function removeEpisode(id: number) {
  if (!confirm(t("admin.confirmDeleteBody"))) return;
  await adminApi.deleteEpisode(id);
  emit("changed");
}

async function togglePublish(ep: any) {
  await adminApi.updateEpisode(ep.id, {
    status: ep.status === "published" ? "draft" : "published",
  });
  emit("changed");
}

async function removeSeason() {
  if (!confirm(t("admin.confirmDeleteBody"))) return;
  await adminApi.deleteSeason(props.season.id);
  emit("changed");
}
</script>

<template>
  <div class="frame p-6">
    <div class="flex items-baseline justify-between mb-6">
      <p class="font-serif text-2xl">{{ t("catalog.season", { n: season.number }) }}</p>
      <button type="button" class="label-caps hover:text-blood-500" @click="removeSeason">
        {{ t("admin.delete") }}
      </button>
    </div>

    <ul class="border-t border-paper-300/20 mb-6">
      <li
        v-for="ep in season.episodes"
        :key="ep.id"
        class="border-b border-paper-300/20 px-2 py-3 flex items-center justify-between"
      >
        <div class="flex items-baseline gap-4">
          <span class="label-caps w-8">{{ String(ep.number).padStart(2, "0") }}</span>
          <span class="font-serif text-lg">{{ ep.title }}</span>
          <span class="label-caps text-paper-300">
            {{ ep.status === "published" ? t("admin.statusPublished") : t("admin.statusDraft") }}
          </span>
        </div>
        <div class="flex items-center gap-4 label-caps">
          <button type="button" class="hover:text-blood-500" @click="togglePublish(ep)">
            {{ ep.status === "published" ? t("admin.unpublish") : t("admin.publish") }}
          </button>
          <button type="button" class="hover:text-blood-500" @click="removeEpisode(ep.id)">
            {{ t("admin.delete") }}
          </button>
        </div>
      </li>
    </ul>

    <div class="flex gap-3 items-end">
      <div class="flex-1">
        <label class="label-caps block mb-2">Episode title</label>
        <input
          v-model="newEpisodeTitle"
          type="text"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-2 text-paper-100 outline-none"
          @keydown.enter.prevent="addEpisode"
        />
      </div>
      <AdminSecondaryButton @click="addEpisode">{{ t("admin.save") }}</AdminSecondaryButton>
    </div>
  </div>
</template>
