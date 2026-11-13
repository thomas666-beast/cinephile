<script setup lang="ts">
defineProps<{
  label: string;
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <header class="mb-8 border-b border-paper-300/20 pb-4">
    <div class="flex items-center justify-between gap-6">
      <div>
        <p class="label-caps text-paper-300 mb-1">{{ label }}</p>
        <h1 class="font-serif text-2xl text-paper-100">{{ title }}</h1>
        <p v-if="subtitle" class="mt-1 text-sm text-paper-300/80">{{ subtitle }}</p>
      </div>
      <div class="flex items-center gap-3 shrink-0">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>
