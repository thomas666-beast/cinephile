<script setup lang="ts">
import { useI18n } from "vue-i18n";
const { t } = useI18n();
</script>

<template>
  <p class="label-caps py-16 text-center">{{ t("common.loading") }}</p>
</template>
