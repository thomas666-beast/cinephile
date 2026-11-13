<script setup lang="ts">
import type { Genre } from "../api/types";
defineProps<{ genres: Genre[] }>();
</script>

<template>
  <ul class="flex flex-wrap gap-x-4 gap-y-2 label-caps">
    <li v-for="g in genres" :key="g.id">{{ g.name }}</li>
  </ul>
</template>
