<script setup lang="ts">
defineProps<{
  label: string;
  htmlFor: string;
  error?: string | null;
  hint?: string | null;
}>();
</script>

<template>
  <div>
    <label :for="htmlFor" class="label-caps block mb-2">{{ label }}</label>
    <slot />
    <p v-if="hint && !error" class="mt-2 text-sm text-paper-300/70">{{ hint }}</p>
    <p v-if="error" class="mt-2 text-sm text-blood-500">{{ error }}</p>
  </div>
</template>
