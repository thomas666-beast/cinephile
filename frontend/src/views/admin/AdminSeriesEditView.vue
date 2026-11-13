<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { adminApi } from "../../api";
import type { Genre } from "../../api/types";
import AdminPageHeader from "../../components/admin/AdminPageHeader.vue";
import AdminField from "../../components/admin/AdminField.vue";
import AdminPrimaryButton from "../../components/admin/AdminPrimaryButton.vue";
import AdminSecondaryButton from "../../components/admin/AdminSecondaryButton.vue";
import SeasonEditor from "../../components/admin/SeasonEditor.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const isNew = computed(() => route.name === "admin-series-new");
const slug = computed(() => (isNew.value ? null : String(route.params.slug)));

const series = ref<any>(null);
const genres = ref<Genre[]>([]);
const loading = ref(true);
const saving = ref(false);
const serverError = ref<string | null>(null);
const newSeasonNumber = ref(1);

const form = reactive({
  title: "",
  synopsis: "",
  start_year: null as number | null,
  end_year: null as number | null,
  genres: [] as number[],
  status: "draft" as "draft" | "published",
});

async function load() {
  loading.value = true;
  try {
    genres.value = await adminApi.listGenres();
    if (!isNew.value && slug.value) {
      const data = await adminApi.getSeries(slug.value);
      series.value = data;
      form.title = data.title;
      form.synopsis = data.synopsis;
      form.start_year = data.start_year;
      form.end_year = data.end_year;
      form.genres = data.genres;
      form.status = data.status;
      newSeasonNumber.value = (data.seasons?.at(-1)?.number ?? 0) + 1;
    }
  } finally {
    loading.value = false;
  }
}

async function onSave() {
  serverError.value = null;
  saving.value = true;
  try {
    const payload = {
      title: form.title.trim(),
      synopsis: form.synopsis,
      start_year: form.start_year ?? undefined,
      end_year: form.end_year ?? undefined,
      genres: form.genres,
      status: form.status,
    };
    if (isNew.value) {
      const created = await adminApi.createSeries(payload);
      router.push(`/admin/series/${created.slug}`);
    } else if (slug.value) {
      await adminApi.updateSeries(slug.value, payload);
      await load();
    }
  } catch (e: any) {
    serverError.value = e?.response?.data?.detail ?? t("common.error");
  } finally {
    saving.value = false;
  }
}

async function addSeason() {
  if (!series.value) return;
  await adminApi.createSeason({ series: series.value.slug, number: newSeasonNumber.value });
  await load();
}

async function togglePublish() {
  if (!slug.value) return;
  const fn = form.status === "published" ? adminApi.unpublishSeries : adminApi.publishSeries;
  const updated = await fn(slug.value);
  form.status = updated.status;
  series.value = updated;
}

onMounted(load);
watch(() => route.fullPath, load);
</script>

<template>
  <div>
    <AdminPageHeader
      :label="t('admin.navSection')"
      :title="isNew ? t('admin.newSeries') : series?.title ?? ''"
    >
      <template #actions>
        <RouterLink to="/admin/series">
          <AdminSecondaryButton>{{ t("common.back") }}</AdminSecondaryButton>
        </RouterLink>
        <AdminPrimaryButton :disabled="saving" @click="onSave">
          {{ saving ? t("admin.saving") : t("admin.save") }}
        </AdminPrimaryButton>
      </template>
    </AdminPageHeader>

    <p v-if="loading" class="label-caps py-16 text-center">{{ t("common.loading") }}</p>

    <form v-else class="grid lg:grid-cols-[1fr_320px] gap-8" @submit.prevent="onSave">
      <div class="space-y-5">
        <AdminField :label="t('admin.colTitle')" html-for="title">
          <input id="title" v-model="form.title" type="text"
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none" />
        </AdminField>

        <AdminField label="Synopsis" html-for="synopsis">
          <textarea id="synopsis" v-model="form.synopsis" rows="6"
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none" />
        </AdminField>

        <div class="grid grid-cols-2 gap-4">
          <AdminField label="Start year" html-for="start_year">
            <input id="start_year" v-model.number="form.start_year" type="number"
              class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none" />
          </AdminField>
          <AdminField label="End year" html-for="end_year">
            <input id="end_year" v-model.number="form.end_year" type="number"
              class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none" />
          </AdminField>
        </div>

        <AdminField label="Genres" html-for="genres">
          <select id="genres" v-model="form.genres" multiple
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none h-40">
            <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </AdminField>

        <p v-if="serverError" class="text-sm text-blood-500">{{ serverError }}</p>
      </div>

      <div class="space-y-5">
        <div class="frame p-5">
          <p class="label-caps mb-2">{{ t("admin.colStatus") }}</p>
          <p class="font-serif text-base mb-4">
            {{ form.status === "published" ? t("admin.statusPublished") : t("admin.statusDraft") }}
          </p>
          <AdminSecondaryButton @click="togglePublish">
            {{ form.status === "published" ? t("admin.unpublish") : t("admin.publish") }}
          </AdminSecondaryButton>
        </div>
      </div>
    </form>

    <section v-if="!isNew && series" class="mt-12">
      <p class="label-caps mb-4">{{ t("catalog.seasons") }}</p>

      <div class="space-y-5">
        <SeasonEditor
          v-for="s in series.seasons"
          :key="s.id"
          :series-id="series.id"
          :season="s"
          @changed="load"
        />
      </div>

      <div class="flex gap-3 items-end mt-6">
        <div>
          <label class="label-caps block mb-2">{{ t("catalog.seasons") }}</label>
          <input v-model.number="newSeasonNumber" type="number"
            class="bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none w-20" />
        </div>
        <AdminSecondaryButton @click="addSeason">Add season</AdminSecondaryButton>
      </div>
    </section>
  </div>
</template>
