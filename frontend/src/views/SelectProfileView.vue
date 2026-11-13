<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { useProfileStore } from "../stores/profiles";

const { t } = useI18n();
const auth = useAuthStore();
const profiles = useProfileStore();
const router = useRouter();

onMounted(async () => {
  if (!auth.user) { router.push({ name: "sign-in" }); return; }
  await profiles.load();
  if (profiles.profiles.length === 0) {
    router.push({ name: "my-account" });
  }
});

function pick(id: number) {
  profiles.setActive(id);
  router.push("/");
}
</script>

<template>
  <section class="max-w-3xl mx-auto px-6 py-24 text-center">
    <p class="label-caps mb-3">{{ t("profiles.selectTitle") }}</p>
    <h1 class="font-serif text-3xl md:text-4xl mb-12">{{ t("profiles.whoseWatching") }}</h1>

    <div class="flex flex-wrap items-start justify-center gap-6">
      <button
        v-for="p in profiles.profiles"
        :key="p.id"
        type="button"
        class="group flex flex-col items-center"
        @click="pick(p.id)"
      >
        <span
          class="w-24 h-24 frame flex items-center justify-center font-serif text-3xl transition-colors"
          :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
          :class="profiles.activeId === p.id ? 'border-blood-500' : 'group-hover:border-paper-100'"
        >
          {{ p.initial }}
        </span>
        <span class="label-caps mt-3">{{ p.name }}</span>
      </button>
    </div>

    <p class="mt-12 label-caps">
      <RouterLink to="/my-account" class="text-paper-300 hover:text-paper-100">
        {{ t("profiles.manageProfiles") }}
      </RouterLink>
    </p>
  </section>
</template>
