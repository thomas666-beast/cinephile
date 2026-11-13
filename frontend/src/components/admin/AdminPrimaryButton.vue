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
    class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-5 py-3 disabled:opacity-60 disabled:cursor-not-allowed"
  >
    <slot />
  </button>
</template>
