<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { computed, onMounted, ref } from "vue";
import { useAuthStore } from "./stores/auth";
import { useProfileStore } from "./stores/profiles";
import { watch } from "vue";

const { t } = useI18n();
const auth = useAuthStore();
const profiles = useProfileStore();
const router = useRouter();
const route = useRoute();

const searchQuery = ref("");

async function onSignOut() {
  await auth.logout();
  profiles.clear();
  
  // Redirect to home page and force a reload to clear any cached state
  if (route.path !== "/") {
    router.push("/");
  } else {
    // If already on home, just reload the page to ensure clean state
    window.location.reload();
  }
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

watch(() => auth.user, (newUser, oldUser) => {
  if (oldUser && !newUser) {
    if (route.path.startsWith("/my-account") || route.path.startsWith("/select-profile")) {
      router.push("/");
    }
  }
});
</script>

<template>
  <div class="min-h-screen flex flex-col bg-noir-950 text-paper-100 selection:bg-blood-500 selection:text-white">
    <header class="border-b border-paper-300/10">
      <!-- Tighter Row 1 -->
      <div class="max-w-7xl mx-auto flex items-center justify-between px-6 py-3">
        <RouterLink to="/" class="flex items-baseline gap-3 shrink-0">
          <span class="font-serif text-2xl tracking-tight">{{ t("common.appName") }}</span>
        </RouterLink>

        <form class="hidden md:flex flex-1 max-w-md mx-12 items-center" @submit.prevent="onSearchSubmit">
          <input
            v-model="searchQuery"
            type="search"
            :placeholder="t('search.placeholder')"
            class="w-full bg-transparent border-b border-paper-300/20 focus:border-paper-100 py-1.5 text-xs text-paper-100 outline-none placeholder:text-paper-300/40 transition-colors"
            :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
          />
        </form>

        <nav class="flex items-center gap-5 label-caps shrink-0">
          <template v-if="!auth.user">
            <RouterLink to="/sign-in" class="text-paper-300 hover:text-paper-100 transition-colors">
              {{ t("nav.signIn") }}
            </RouterLink>
            <RouterLink to="/register" class="text-paper-100 border-b border-blood-500 pb-0.5">
              {{ t("nav.register") }}
            </RouterLink>
          </template>
          <template v-else>
            <span v-if="profiles.active" class="text-paper-300 flex items-center gap-2">
              <span class="w-5 h-5 frame flex items-center justify-center font-serif text-xs">
                {{ profiles.active.initial }}
              </span>
              {{ profiles.active.name }}
            </span>
            <RouterLink v-if="profiles.profiles.length > 0" to="/select-profile" class="text-paper-300 hover:text-paper-100">
              {{ t("nav.switch") }}
            </RouterLink>
            <RouterLink to="/my-account" class="text-paper-300 hover:text-paper-100">
              {{ t("nav.myAccount") }}
            </RouterLink>
            <button type="button" class="text-paper-300 hover:text-paper-100" @click="onSignOut">
              {{ t("nav.signOut") }}
            </button>
          </template>
        </nav>
      </div>

      <!-- Tighter Row 2 -->
      <div class="border-t border-paper-300/10">
        <nav class="max-w-7xl mx-auto px-6 py-2 flex justify-center">
          <ul class="flex flex-wrap items-center gap-x-2 gap-y-1">
            <template v-for="(item, index) in sections" :key="item.to">
              <li v-if="index > 0" class="text-paper-300/30 label-caps select-none text-xs" aria-hidden="true">|</li>
              <li>
                <RouterLink
                  :to="item.to"
                  class="label-caps px-3 py-1 text-xs transition-colors"
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

    <footer class="border-t border-paper-300/10">
      <div class="max-w-7xl mx-auto px-6 py-4 label-caps flex justify-between text-xs text-paper-300/60">
        <span>{{ t("common.appName") }}</span>
        <span>© {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>
