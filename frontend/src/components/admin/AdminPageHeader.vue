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
    <div class="flex items-baseline justify-between gap-6">
      <h1 class="font-serif text-3xl md:text-4xl leading-tight">{{ title }}</h1>
      <div class="flex items-center gap-3 shrink-0">
        <slot name="actions" />
      </div>
    </div>
    <p v-if="subtitle" class="mt-2 text-paper-300 max-w-2xl">{{ subtitle }}</p>
  </header>
</template>
