<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { adminApi } from "../../api";
import type { Genre } from "../../api/types";
import AdminPageHeader from "../../components/admin/AdminPageHeader.vue";
import AdminPrimaryButton from "../../components/admin/AdminPrimaryButton.vue";

const { t } = useI18n();
const genres = ref<Genre[]>([]);
const loading = ref(true);
const newName = ref("");

async function load() {
  loading.value = true;
  try { genres.value = await adminApi.listGenres(); }
  finally { loading.value = false; }
}

async function create() {
  if (!newName.value.trim()) return;
  await adminApi.createGenre({ name: newName.value.trim() });
  newName.value = "";
  load();
}

async function remove(id: number) {
  if (!confirm(t("admin.confirmDeleteBody"))) return;
  await adminApi.deleteGenre(id);
  load();
}

onMounted(load);
</script>

<template>
  <div>
    <AdminPageHeader :label="t('admin.navSection')" :title="t('admin.listGenresTitle')">
      <template #actions>
        <form class="flex gap-2 items-end" @submit.prevent="create">
          <input
            v-model="newName"
            type="text"
            placeholder="New genre"
            class="bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none text-sm"
          />
          <AdminPrimaryButton type="submit">Add</AdminPrimaryButton>
        </form>
      </template>
    </AdminPageHeader>

    <div class="frame">
      <ul class="divide-y divide-paper-300/15">
        <li v-if="loading" class="px-4 py-6 text-center label-caps">{{ t("common.loading") }}</li>
        <li v-else-if="genres.length === 0" class="px-4 py-6 text-center label-caps">{{ t("admin.noRows") }}</li>
        <li
          v-for="g in genres"
          :key="g.id"
          class="px-4 py-3 flex items-center justify-between"
        >
          <span class="font-serif text-base">{{ g.name }}</span>
          <button type="button" class="label-caps hover:text-blood-500" @click="remove(g.id)">
            {{ t("admin.delete") }}
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
