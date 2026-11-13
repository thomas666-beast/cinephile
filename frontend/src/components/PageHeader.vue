<script setup lang="ts">
defineProps<{
  label: string;
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <header class="mb-10">
    <p class="label-caps mb-2">{{ label }}</p>
    <h1 class="font-serif text-3xl md:text-4xl leading-[1.05]">{{ title }}</h1>
    <p v-if="subtitle" class="mt-3 text-paper-300 max-w-xl">{{ subtitle }}</p>
  </header>
</template>
