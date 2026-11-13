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
    class="block group"
  >
    <!-- Poster: larger aspect ratio, no border, image is the star -->
    <div class="relative aspect-[2/3] bg-noir-800 overflow-hidden">
      <img
        v-if="imageSrc"
        :src="imageSrc"
        :alt="title"
        loading="lazy"
        class="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.03]"
      />
      <!-- Subtle gradient at bottom for title legibility -->
      <div class="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-noir-950/90 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <!-- Title overlays on hover -->
      <div class="absolute inset-x-0 bottom-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <p class="font-serif text-lg text-paper-100 leading-tight">{{ title }}</p>
        <p v-if="meta" class="label-caps mt-1 text-paper-300">{{ meta }}</p>
      </div>
    </div>
    <!-- Title below (visible when not hovering) -->
    <div class="mt-3 group-hover:opacity-0 transition-opacity duration-300">
      <p class="font-serif text-lg text-paper-100 leading-tight">{{ title }}</p>
      <p v-if="meta" class="label-caps mt-1 text-paper-300 text-xs">{{ meta }}</p>
    </div>
  </RouterLink>
</template>
