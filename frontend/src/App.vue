<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView } from "vue-router";
import { useAuthStore } from "./stores/auth";
import { useRouter } from "vue-router";

const { t } = useI18n();
const auth = useAuthStore();
const router = useRouter();

async function onSignOut() {
  await auth.logout();
  router.push("/");
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-noir-950 text-paper-100">
    <header class="border-b border-paper-300/20">
      <nav class="max-w-6xl mx-auto flex items-center justify-between px-6 py-5">
        <RouterLink to="/" class="flex items-baseline gap-3">
          <span class="font-serif text-2xl tracking-tight">{{ t("common.appName") }}</span>
          <span class="label-caps hidden sm:inline">Cinema &amp; Series</span>
        </RouterLink>

        <ul class="flex items-center gap-6 label-caps">
          <li><RouterLink to="/">{{ t("nav.home") }}</RouterLink></li>
          <li><RouterLink to="/movies">{{ t("nav.movies") }}</RouterLink></li>
          <li><RouterLink to="/series">{{ t("nav.series") }}</RouterLink></li>
          <li v-if="!auth.user">
            <RouterLink to="/sign-in">{{ t("nav.signIn") }}</RouterLink>
          </li>
          <li v-if="!auth.user">
            <RouterLink to="/register" class="text-paper-100 border-b border-blood-500 pb-0.5">
              {{ t("nav.register") }}
            </RouterLink>
          </li>
          <li v-if="auth.user">
            <span class="text-paper-300">{{ auth.user.first_name || auth.user.email }}</span>
          </li>
          <li v-if="auth.user">
            <button type="button" class="hover:text-paper-100" @click="onSignOut">
              {{ t("nav.signOut") }}
            </button>
          </li>
        </ul>
      </nav>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <footer class="border-t border-paper-300/20">
      <div class="max-w-6xl mx-auto px-6 py-6 label-caps flex justify-between">
        <span>{{ t("common.appName") }}</span>
        <span>© {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
nav :deep(a.router-link-exact-active) {
  color: var(--color-paper-100);
  border-bottom: 1px solid var(--color-blood-500);
  padding-bottom: 2px;
}
</style>
