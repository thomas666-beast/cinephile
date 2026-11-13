<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { adminApi } from "../../api";
import type { MovieListItem } from "../../api/types";
import AdminPageHeader from "../../components/admin/AdminPageHeader.vue";
import AdminPrimaryButton from "../../components/admin/AdminPrimaryButton.vue";
import AdminSecondaryButton from "../../components/admin/AdminSecondaryButton.vue";

const { t } = useI18n();
const router = useRouter();

interface AdminMovieRow extends MovieListItem {
  status: "draft" | "published";
  video_status: { id: number; status: string; processing_error: string | null } | null;
}

const rows = ref<AdminMovieRow[]>([]);
const loading = ref(true);
const search = ref("");
const statusFilter = ref<"" | "draft" | "published">("");

async function load() {
  loading.value = true;
  try {
    const data = await adminApi.listMovies({
      search: search.value || undefined,
      status: statusFilter.value || undefined,
    });
    rows.value = data.results;
  } finally {
    loading.value = false;
  }
}

async function onPublish(slug: string) {
  await adminApi.publishMovie(slug);
  load();
}

async function onUnpublish(slug: string) {
  await adminApi.unpublishMovie(slug);
  load();
}

async function onDelete(slug: string) {
  if (!confirm(t("admin.confirmDeleteBody"))) return;
  await adminApi.deleteMovie(slug);
  load();
}

onMounted(load);

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
watch(search, () => {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(load, 300);
});
watch(statusFilter, load);

function videoStateLabel(row: AdminMovieRow): string {
  if (!row.video_status) return t("admin.statusNoVideo");
  return {
    ready: t("admin.ready"),
    processing: t("admin.processing"),
    failed: t("admin.failed"),
    pending: t("admin.processing"),
    uploaded: t("admin.processing"),
  }[row.video_status.status] ?? row.video_status.status;
}
</script>

<template>
  <div>
    <AdminPageHeader :label="t('admin.navSection')" :title="t('admin.listMoviesTitle')">
      <template #actions>
        <RouterLink to="/admin/movies/new">
          <AdminPrimaryButton>{{ t("admin.newMovie") }}</AdminPrimaryButton>
        </RouterLink>
      </template>
    </AdminPageHeader>

    <div class="flex flex-wrap gap-4 mb-8 items-end">
      <div class="flex-1 min-w-[200px]">
        <label for="search" class="label-caps block mb-2">{{ t("admin.searchPlaceholder") }}</label>
        <input
          id="search"
          v-model="search"
          type="search"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-2 text-paper-100 outline-none"
        />
      </div>
      <div>
        <label for="status" class="label-caps block mb-2">{{ t("admin.colStatus") }}</label>
        <select
          id="status"
          v-model="statusFilter"
          class="bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-2 text-paper-100 outline-none"
        >
          <option value="">{{ t("admin.filterAll") }}</option>
          <option value="draft">{{ t("admin.statusDraft") }}</option>
          <option value="published">{{ t("admin.statusPublished") }}</option>
        </select>
      </div>
    </div>

    <div class="frame">
      <table class="w-full text-left">
        <thead>
          <tr class="border-b border-paper-300/20">
            <th class="label-caps px-5 py-4">{{ t("admin.colTitle") }}</th>
            <th class="label-caps px-5 py-4">{{ t("admin.colYear") }}</th>
            <th class="label-caps px-5 py-4">{{ t("admin.colStatus") }}</th>
            <th class="label-caps px-5 py-4">{{ t("admin.colVideo") }}</th>
            <th class="label-caps px-5 py-4 text-right">{{ t("admin.colActions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-5 py-8 text-center label-caps">{{ t("common.loading") }}</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="5" class="px-5 py-8 text-center label-caps">{{ t("admin.noRows") }}</td>
          </tr>
          <tr
            v-for="row in rows"
            :key="row.id"
            class="border-b border-paper-300/15 last:border-b-0"
          >
            <td class="px-5 py-4 font-serif text-lg">{{ row.title }}</td>
            <td class="px-5 py-4 label-caps">{{ row.release_year ?? "—" }}</td>
            <td class="px-5 py-4 label-caps">
              {{ row.status === "published" ? t("admin.statusPublished") : t("admin.statusDraft") }}
            </td>
            <td class="px-5 py-4 label-caps">{{ videoStateLabel(row) }}</td>
            <td class="px-5 py-4 text-right">
              <div class="flex items-center justify-end gap-4 label-caps">
                <RouterLink :to="`/admin/movies/${row.slug}`" class="hover:text-paper-100">
                  {{ t("admin.edit") }}
                </RouterLink>
                <button
                  v-if="row.status === 'draft'"
                  type="button"
                  class="hover:text-blood-500"
                  @click="onPublish(row.slug)"
                >
                  {{ t("admin.publish") }}
                </button>
                <button
                  v-else
                  type="button"
                  class="hover:text-paper-100"
                  @click="onUnpublish(row.slug)"
                >
                  {{ t("admin.unpublish") }}
                </button>
                <button
                  type="button"
                  class="hover:text-blood-500"
                  @click="onDelete(row.slug)"
                >
                  {{ t("admin.delete") }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
