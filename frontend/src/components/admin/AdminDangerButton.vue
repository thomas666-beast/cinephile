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
    class="frame px-5 py-3 label-caps hover:border-blood-500 hover:text-blood-500 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
    :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
  >
    <slot />
  </button>
</template>
