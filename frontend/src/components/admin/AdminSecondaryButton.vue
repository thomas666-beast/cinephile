<script setup lang="ts">
defineProps<{
  type?: "button" | "submit";
  disabled?: boolean;
}>();
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="disabled"
    class="frame px-4 py-2 label-caps hover:border-paper-100 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
    :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
  >
    <slot />
  </button>
</template>
