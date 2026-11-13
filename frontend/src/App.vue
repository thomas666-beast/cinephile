<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView } from "vue-router";

const { t } = useI18n();
</script>

<template>
  <div class="min-h-screen flex flex-col bg-noir-950 text-paper-100">
    <!-- Header -->
    <header class="border-b border-paper-300/20">
      <nav class="max-w-6xl mx-auto flex items-center justify-between px-6 py-5">
        <RouterLink to="/" class="flex items-baseline gap-3">
          <span class="font-serif text-2xl tracking-tight">{{ t("common.appName") }}</span>
          <span class="label-caps hidden sm:inline">Cinema &amp; Series</span>
        </RouterLink>
        <ul class="flex items-center gap-6 label-caps">
          <li><RouterLink to="/">{{ t("nav.home") }}</RouterLink></li>
          <!-- More nav added with the screens that back them -->
        </ul>
      </nav>
    </header>

    <!-- Main -->
    <main class="flex-1">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="border-t border-paper-300/20">
      <div class="max-w-6xl mx-auto px-6 py-6 label-caps flex justify-between">
        <span>{{ t("common.appName") }}</span>
        <span>© {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>
