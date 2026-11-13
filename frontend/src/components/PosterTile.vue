<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

const props = defineProps<{
  to: { name: string; params: { slug: string } };
  title: string;
  posterUrl: string | null;
  meta: string | null;   // pre-formatted (e.g., "2010" or "2017–2024")
}>();

const imageSrc = computed(() => props.posterUrl ?? "");
</script>

<template>
  <RouterLink
    :to="to"
    class="block frame group"
  >
    <div class="aspect-[2/3] bg-noir-800 overflow-hidden">
      <img
        v-if="imageSrc"
        :src="imageSrc"
        :alt="title"
        loading="lazy"
        class="w-full h-full object-cover"
      />
    </div>
    <div class="p-3 border-t border-paper-300/20">
      <p class="font-serif text-lg leading-tight">{{ title }}</p>
      <p v-if="meta" class="label-caps mt-1">{{ meta }}</p>
    </div>
  </RouterLink>
</template>

<style scoped>
/* The one permitted motion: a slow image dim on hover, not a lift or shadow. */
.group:hover img {
  opacity: 0.85;
  transition: opacity var(--duration-quick) var(--ease-hitchcock);
}
</style>
