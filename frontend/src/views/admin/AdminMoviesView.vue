<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { adminApi } from "../../api";
import type { MovieListItem } from "../../api/types";
import AdminPageHeader from "../../components/admin/AdminPageHeader.vue";
import AdminPrimaryButton from "../../components/admin/AdminPrimaryButton.vue";

const { t } = useI18n();

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

async function onPublish(slug: string) { await adminApi.publishMovie(slug); load(); }
async function onUnpublish(slug: string) { await adminApi.unpublishMovie(slug); load(); }

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

    <div class="flex items-end gap-4 mb-4">
      <div class="flex-1 max-w-xs">
        <input
          v-model="search"
          type="search"
          :placeholder="t('admin.searchPlaceholder')"
          class="w-full bg-transparent border border-paper-300/30 focus:border-paper-100 px-3 py-1.5 text-sm text-paper-100 outline-none"
        />
      </div>
      <div>
        <select
          v-model="statusFilter"
          class="bg-transparent border border-paper-300/30 focus:border-paper-100 px-3 py-1.5 text-sm text-paper-100 outline-none"
        >
          <option value="">{{ t("admin.filterAll") }}</option>
          <option value="draft">{{ t("admin.statusDraft") }}</option>
          <option value="published">{{ t("admin.statusPublished") }}</option>
        </select>
      </div>
    </div>

    <div class="border border-paper-300/20">
      <table class="w-full text-left text-sm">
        <thead class="bg-noir-900 border-b border-paper-300/20">
          <tr>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colTitle") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colYear") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colStatus") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colVideo") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300 text-right">{{ t("admin.colActions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-4 py-12 text-center label-caps text-paper-300/60">{{ t("common.loading") }}</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="5" class="px-4 py-12 text-center label-caps text-paper-300/60">{{ t("admin.noRows") }}</td>
          </tr>
          <tr
            v-for="row in rows"
            :key="row.id"
            class="border-b border-paper-300/10 last:border-b-0 hover:bg-noir-800/40 transition-colors"
          >
            <td class="px-4 py-2 text-paper-100">{{ row.title }}</td>
            <td class="px-4 py-2 text-paper-300">{{ row.release_year ?? "—" }}</td>
            <td class="px-4 py-2">
              <span class="inline-block w-2 h-2 rounded-full mr-2" :class="row.status === 'published' ? 'bg-green-500' : 'bg-yellow-500'" />
              <span class="text-paper-300">{{ row.status === "published" ? t("admin.statusPublished") : t("admin.statusDraft") }}</span>
            </td>
            <td class="px-4 py-2 text-paper-300">{{ videoStateLabel(row) }}</td>
            <td class="px-4 py-2 text-right">
              <div class="flex items-center justify-end gap-3 label-caps text-xs">
                <RouterLink :to="`/admin/movies/${row.slug}`" class="text-paper-300 hover:text-paper-100">
                  {{ t("admin.edit") }}
                </RouterLink>
                <button v-if="row.status === 'draft'" type="button" class="text-paper-300 hover:text-paper-100" @click="onPublish(row.slug)">
                  {{ t("admin.publish") }}
                </button>
                <button v-else type="button" class="text-paper-300 hover:text-paper-100" @click="onUnpublish(row.slug)">
                  {{ t("admin.unpublish") }}
                </button>
                <button type="button" class="text-paper-300 hover:text-blood-500" @click="onDelete(row.slug)">
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
