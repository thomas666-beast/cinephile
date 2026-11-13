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
  <div class="max-w-7xl mx-auto px-6 py-12 grid md:grid-cols-[200px_1fr] gap-10">
    <aside>
      <p class="label-caps mb-3">{{ t("admin.navSection") }}</p>
      <nav>
        <ul class="border-t border-paper-300/20">
          <li
            v-for="item in navItems"
            :key="item.to"
            class="border-b border-paper-300/20"
          >
            <RouterLink
              :to="item.to"
              class="block px-3 py-2.5 label-caps transition-colors"
              :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
              :class="isActive(item)
                ? 'text-paper-100 border-l-2 border-blood-500'
                : 'text-paper-300 hover:text-paper-100 border-l-2 border-transparent'"
            >
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </nav>
    </aside>

    <main>
      <RouterView />
    </main>
  </div>
</template>
