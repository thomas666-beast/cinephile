<script setup lang="ts" generic="T extends { id: number | string }">
defineProps<{
  columns: { key: string; label: string; class?: string }[];
  rows: T[];
  loading?: boolean;
}>();
</script>

<template>
  <div class="frame">
    <table class="w-full text-left">
      <thead>
        <tr class="border-b border-paper-300/20">
          <th
            v-for="col in columns"
            :key="col.key"
            class="label-caps px-5 py-4"
            :class="col.class"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length" class="px-5 py-8 text-center label-caps">
            Loading…
          </td>
        </tr>
        <tr v-else-if="rows.length === 0">
          <td :colspan="columns.length" class="px-5 py-8 text-center label-caps">
            <slot name="empty">No items yet.</slot>
          </td>
        </tr>
        <tr
          v-else
          v-for="row in rows"
          :key="row.id"
          class="border-b border-paper-300/15 last:border-b-0"
        >
          <slot name="row" :row="row" />
        </tr>
      </tbody>
    </table>
  </div>
</template>
