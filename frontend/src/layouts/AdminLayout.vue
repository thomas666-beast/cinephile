<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { computed } from "vue";

const { t } = useI18n();
const route = useRoute();

const navItems = computed(() => [
  { to: "/admin", label: t("admin.dashboard"), exact: true },
  { to: "/admin/movies", label: t("admin.movies") },
  { to: "/admin/series", label: t("admin.series") },
  { to: "/admin/plans", label: t("admin.plans") },
  { to: "/admin/genres", label: t("admin.genres") },
]);

function isActive(item: { to: string; exact?: boolean }): boolean {
  if (item.exact) return route.path === item.to;
  return route.path === item.to || route.path.startsWith(item.to + "/");
}
</script>

<template>
  <div class="max-w-[1400px] mx-auto px-6 py-8 grid md:grid-cols-[200px_1fr] gap-8">
    <aside class="border-r border-paper-300/10 pr-6">
      <p class="label-caps text-paper-300/60 mb-4">{{ t("admin.navSection") }}</p>
      <nav>
        <ul class="space-y-1">
          <li v-for="item in navItems" :key="item.to">
            <RouterLink
              :to="item.to"
              class="block px-3 py-2 text-sm transition-colors border-l-2"
              :class="isActive(item)
                ? 'text-paper-100 border-blood-500 bg-noir-800/50 font-medium'
                : 'text-paper-300 border-transparent hover:text-paper-100 hover:bg-noir-800/30'"
            >
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </nav>
    </aside>

    <main class="min-w-0">
      <RouterView />
    </main>
  </div>
</template>
