<script setup lang="ts">
defineProps<{
  label: string;
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <header class="mb-12">
    <p class="label-caps mb-3">{{ label }}</p>
    <h1 class="font-serif text-4xl md:text-5xl leading-[1.05]">{{ title }}</h1>
    <p v-if="subtitle" class="mt-4 text-paper-300 max-w-xl">{{ subtitle }}</p>
  </header>
</template>
