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
    class="frame px-5 py-3 label-caps hover:border-paper-100 disabled:opacity-60 disabled:cursor-not-allowed"
  >
    <slot />
  </button>
</template>
