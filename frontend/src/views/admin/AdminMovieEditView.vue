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
import VideoUploadWidget from "../../components/admin/VideoUploadWidget.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const isNew = computed(() => route.name === "admin-movie-new");
const slug = computed(() => (isNew.value ? null : String(route.params.slug)));

interface MovieData {
  id: number;
  title: string;
  slug: string;
  synopsis: string;
  release_year: number | null;
  duration_minutes: number | null;
  genres: number[];
  genre_names: string[];
  poster: string | null;
  backdrop: string | null;
  status: "draft" | "published";
  video_status: { id: number; status: string; processing_error: string | null } | null;
}

const movie = ref<MovieData | null>(null);
const genres = ref<Genre[]>([]);
const loading = ref(true);
const saving = ref(false);
const serverError = ref<string | null>(null);
const errors = reactive<Record<string, string>>({});

const form = reactive({
  title: "",
  synopsis: "",
  release_year: null as number | null,
  duration_minutes: null as number | null,
  genres: [] as number[],
  status: "draft" as "draft" | "published",
});

async function load() {
  loading.value = true;
  try {
    genres.value = await adminApi.listGenres();
    if (!isNew.value && slug.value) {
      const data = await adminApi.getMovie(slug.value);
      movie.value = data;
      form.title = data.title;
      form.synopsis = data.synopsis;
      form.release_year = data.release_year;
      form.duration_minutes = data.duration_minutes;
      form.genres = data.genres;
      form.status = data.status;
    }
  } finally {
    loading.value = false;
  }
}

function validate(): boolean {
  errors.title = "";
  if (!form.title.trim()) { errors.title = t("admin.requiredField"); return false; }
  return true;
}

async function onSave() {
  serverError.value = null;
  if (!validate()) return;
  saving.value = true;
  try {
    const payload = {
      title: form.title.trim(),
      synopsis: form.synopsis,
      release_year: form.release_year ?? undefined,
      duration_minutes: form.duration_minutes ?? undefined,
      genres: form.genres,
      status: form.status,
    };
    if (isNew.value) {
      const created = await adminApi.createMovie(payload);
      router.push(`/admin/movies/${created.slug}`);
    } else if (slug.value) {
      const updated = await adminApi.updateMovie(slug.value, payload);
      movie.value = updated;
    }
  } catch (e: any) {
    serverError.value = e?.response?.data?.detail ?? t("common.error");
  } finally {
    saving.value = false;
  }
}

async function onPosterChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file || !slug.value) return;
  await adminApi.uploadMoviePoster(slug.value, file);
  await load();
}

async function onBackdropChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file || !slug.value) return;
  await adminApi.uploadMovieBackdrop(slug.value, file);
  await load();
}

async function onToggleStatus() {
  if (!slug.value) return;
  const fn = form.status === "published" ? adminApi.unpublishMovie : adminApi.publishMovie;
  const updated = await fn(slug.value);
  movie.value = updated;
  form.status = updated.status;
}

async function onDelete() {
  if (!slug.value) return;
  if (!confirm(t("admin.confirmDeleteBody"))) return;
  await adminApi.deleteMovie(slug.value);
  router.push("/admin/movies");
}

onMounted(load);
watch(() => route.fullPath, load);
</script>

<template>
  <div>
    <AdminPageHeader
      :label="t('admin.navSection')"
      :title="isNew ? t('admin.newMovie') : movie?.title ?? ''"
    >
      <template #actions>
        <RouterLink to="/admin/movies">
          <AdminSecondaryButton>{{ t("common.back") }}</AdminSecondaryButton>
        </RouterLink>
        <AdminPrimaryButton :disabled="saving" @click="onSave">
          {{ saving ? t("admin.saving") : isNew ? t("admin.creating") : t("admin.save") }}
        </AdminPrimaryButton>
      </template>
    </AdminPageHeader>

    <p v-if="loading" class="label-caps py-16 text-center">{{ t("common.loading") }}</p>

    <form v-else class="grid lg:grid-cols-[1fr_320px] gap-8" @submit.prevent="onSave">
      <div class="space-y-5">
        <AdminField :label="t('admin.colTitle')" html-for="title" :error="errors.title">
          <input id="title" v-model="form.title" type="text"
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none"
            :class="{ 'border-blood-500': errors.title }" />
        </AdminField>

        <AdminField label="Synopsis" html-for="synopsis">
          <textarea id="synopsis" v-model="form.synopsis" rows="6"
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none" />
        </AdminField>

        <div class="grid grid-cols-2 gap-4">
          <AdminField :label="t('admin.colYear')" html-for="release_year">
            <input id="release_year" v-model.number="form.release_year" type="number"
              class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none" />
          </AdminField>
          <AdminField label="Duration (min)" html-for="duration">
            <input id="duration" v-model.number="form.duration_minutes" type="number"
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
          <AdminSecondaryButton @click="onToggleStatus">
            {{ form.status === "published" ? t("admin.unpublish") : t("admin.publish") }}
          </AdminSecondaryButton>
        </div>

        <template v-if="!isNew && movie">
          <div class="frame p-5">
            <p class="label-caps mb-2">Poster</p>
            <img v-if="movie.poster" :src="movie.poster" alt="" class="w-full mb-3" />
            <input type="file" accept="image/*" class="w-full text-xs text-paper-300" @change="onPosterChange" />
          </div>

          <div class="frame p-5">
            <p class="label-caps mb-2">Backdrop</p>
            <img v-if="movie.backdrop" :src="movie.backdrop" alt="" class="w-full mb-3" />
            <input type="file" accept="image/*" class="w-full text-xs text-paper-300" @change="onBackdropChange" />
          </div>

          <VideoUploadWidget
            :movie-id="movie.id"
            :current-status="(movie.video_status?.status as any) ?? null"
            :current-error="movie.video_status?.processing_error ?? null"
            @updated="load"
          />

          <div>
            <AdminSecondaryButton @click="onDelete">{{ t("admin.delete") }}</AdminSecondaryButton>
          </div>
        </template>
      </div>
    </form>
  </div>
</template>
