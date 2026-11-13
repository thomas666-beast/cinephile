<script setup lang="ts">
defineProps<{ message: string }>();
</script>

<template>
  <div class="frame px-8 py-16 text-center">
    <p class="label-caps">{{ message }}</p>
  </div>
</template>
