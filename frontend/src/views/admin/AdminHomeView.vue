<script setup lang="ts">
import { onMounted } from "vue";
import { RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAdminStore } from "../../stores/admin";
import AdminPageHeader from "../../components/admin/AdminPageHeader.vue";
import AdminPrimaryButton from "../../components/admin/AdminPrimaryButton.vue";

const { t } = useI18n();
const admin = useAdminStore();

onMounted(() => admin.loadStats());
</script>

<template>
  <div>
    <AdminPageHeader
      :label="t('admin.navSection')"
      :title="t('admin.dashboardTitle')"
      :subtitle="t('admin.dashboardSubtitle')"
    >
      <template #actions>
        <RouterLink to="/admin/movies/new">
          <AdminPrimaryButton>{{ t("admin.newMovie") }}</AdminPrimaryButton>
        </RouterLink>
      </template>
    </AdminPageHeader>

    <div v-if="admin.statsLoading" class="label-caps py-16 text-center">
      {{ t("common.loading") }}
    </div>

    <template v-else-if="admin.stats">
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <RouterLink to="/admin/movies" class="frame p-5 hover:border-paper-100 transition-colors">
          <p class="label-caps mb-2">{{ t("admin.statsMovies") }}</p>
          <p class="font-serif text-4xl leading-none">{{ admin.stats.movies.total }}</p>
          <p class="label-caps mt-3 text-paper-300">
            {{ admin.stats.movies.published }} {{ t("admin.published") }} ·
            {{ admin.stats.movies.draft }} {{ t("admin.drafts") }}
          </p>
        </RouterLink>

        <RouterLink to="/admin/series" class="frame p-5 hover:border-paper-100 transition-colors">
          <p class="label-caps mb-2">{{ t("admin.statsSeries") }}</p>
          <p class="font-serif text-4xl leading-none">{{ admin.stats.series.total }}</p>
          <p class="label-caps mt-3 text-paper-300">
            {{ admin.stats.series.published }} {{ t("admin.published") }} ·
            {{ admin.stats.series.draft }} {{ t("admin.drafts") }}
          </p>
        </RouterLink>

        <div class="frame p-5">
          <p class="label-caps mb-2">{{ t("admin.statsVideos") }}</p>
          <p class="font-serif text-4xl leading-none">
            {{ admin.stats.videos.ready + admin.stats.videos.processing + admin.stats.videos.failed }}
          </p>
          <p class="label-caps mt-3 text-paper-300">
            {{ admin.stats.videos.ready }} {{ t("admin.ready") }} ·
            {{ admin.stats.videos.processing }} {{ t("admin.processing") }} ·
            {{ admin.stats.videos.failed }} {{ t("admin.failed") }}
          </p>
        </div>

        <div class="frame p-5">
          <p class="label-caps mb-2">{{ t("admin.statsUsers") }}</p>
          <p class="font-serif text-4xl leading-none">{{ admin.stats.users.total }}</p>
        </div>

        <div class="frame p-5">
          <p class="label-caps mb-2">{{ t("admin.statsActiveSubs") }}</p>
          <p class="font-serif text-4xl leading-none">{{ admin.stats.subscriptions.active }}</p>
        </div>
      </div>
    </template>
  </div>
</template>
