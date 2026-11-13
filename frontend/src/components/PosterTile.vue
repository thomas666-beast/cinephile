<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

const props = defineProps<{
  to: { name: string; params: { slug: string } };
  title: string;
  posterUrl: string | null;
  meta: string | null;
}>();

const imageSrc = computed(() => props.posterUrl ?? "");
</script>

<template>
  <RouterLink
    :to="to"
    class="block frame group transition-colors"
    :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
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
      <p class="font-serif text-base leading-tight">{{ title }}</p>
      <p v-if="meta" class="label-caps mt-1">{{ meta }}</p>
    </div>
  </RouterLink>
</template>

<style scoped>
.group:hover {
  border-color: var(--color-paper-100);
}
</style>
