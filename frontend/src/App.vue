<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { computed, onMounted, ref } from "vue";
import { useAuthStore } from "./stores/auth";
import { useProfileStore } from "./stores/profiles";

const { t } = useI18n();
const auth = useAuthStore();
const profiles = useProfileStore();
const router = useRouter();
const route = useRoute();

const searchQuery = ref("");

async function onSignOut() {
  await auth.logout();
  profiles.clear();
  router.push("/");
}

function onSearchSubmit() {
  if (!searchQuery.value.trim()) return;
  router.push({ name: "search", query: { q: searchQuery.value.trim() } });
  searchQuery.value = "";
}

onMounted(async () => {
  if (auth.user) {
    await profiles.load();
    if (profiles.profiles.length > 0 && !profiles.activeId) {
      router.push({ name: "select-profile" });
    }
  }
});

const sections = computed(() => [
  { to: "/", label: t("nav.home"), exact: true },
  { to: "/movies", label: t("nav.movies") },
  { to: "/series", label: t("nav.series") },
  { to: "/plans", label: t("nav.plans") },
]);

function isActive(item: { to: string; exact?: boolean }): boolean {
  if (item.exact) return route.path === item.to;
  return route.path === item.to || route.path.startsWith(item.to + "/");
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-noir-950 text-paper-100">
    <header class="border-b border-paper-300/20">
      <!-- Row 1: wordmark + search + auth actions -->
      <div class="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
        <!-- Left: Wordmark -->
        <RouterLink to="/" class="flex items-baseline gap-3 shrink-0">
          <span class="font-serif text-2xl tracking-tight">{{ t("common.appName") }}</span>
        </RouterLink>

        <!-- Center: Search -->
        <form class="hidden md:flex flex-1 max-w-sm mx-8 items-center" @submit.prevent="onSearchSubmit">
          <input
            v-model="searchQuery"
            type="search"
            :placeholder="t('search.placeholder')"
            class="w-full bg-transparent border-b border-paper-300/30 focus:border-paper-100 py-1.5 text-sm text-paper-100 outline-none placeholder:text-paper-300/50 transition-colors"
            :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
          />
        </form>

        <!-- Right: Auth + Profile -->
        <nav class="flex items-center gap-6 label-caps shrink-0">
          <template v-if="!auth.user">
            <RouterLink
              to="/sign-in"
              class="text-paper-300 hover:text-paper-100 transition-colors"
              :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
            >
              {{ t("nav.signIn") }}
            </RouterLink>
            <RouterLink
              to="/register"
              class="text-paper-100 border-b border-blood-500 pb-0.5"
            >
              {{ t("nav.register") }}
            </RouterLink>
          </template>
          <template v-else>
            <!-- Active profile chip -->
            <span
              v-if="profiles.active"
              class="text-paper-300 flex items-center gap-2 cursor-default"
            >
              <span class="w-5 h-5 frame flex items-center justify-center font-serif text-xs">
                {{ profiles.active.initial }}
              </span>
              {{ profiles.active.name }}
            </span>
            <!-- Switch profile -->
            <RouterLink
              v-if="profiles.profiles.length > 0"
              to="/select-profile"
              class="text-paper-300 hover:text-paper-100 transition-colors"
              :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
            >
              {{ t("nav.switch") }}
            </RouterLink>
            <!-- My account -->
            <RouterLink
              to="/my-account"
              class="text-paper-300 hover:text-paper-100 transition-colors"
              :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
            >
              {{ t("nav.myAccount") }}
            </RouterLink>
            <!-- Sign out -->
            <button
              type="button"
              class="text-paper-300 hover:text-paper-100 transition-colors"
              :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
              @click="onSignOut"
            >
              {{ t("nav.signOut") }}
            </button>
          </template>
        </nav>
      </div>

      <!-- Row 2: Section strip, centered, hairline-framed -->
      <div class="border-t border-paper-300/15">
        <nav class="max-w-6xl mx-auto px-6 py-3 flex justify-center">
          <ul class="flex flex-wrap items-center gap-x-1 gap-y-1">
            <template v-for="(item, index) in sections" :key="item.to">
              <li v-if="index > 0" class="text-paper-300/40 label-caps select-none" aria-hidden="true">|</li>
              <li>
                <RouterLink
                  :to="item.to"
                  class="label-caps px-3 py-1 transition-colors"
                  :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
                  :class="isActive(item)
                    ? 'text-paper-100 border-b border-blood-500'
                    : 'text-paper-300 hover:text-paper-100 border-b border-transparent'"
                >
                  {{ item.label }}
                </RouterLink>
              </li>
            </template>
          </ul>
        </nav>
      </div>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <footer class="border-t border-paper-300/20">
      <div class="max-w-6xl mx-auto px-6 py-5 label-caps flex justify-between">
        <span>{{ t("common.appName") }}</span>
        <span>© {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>
