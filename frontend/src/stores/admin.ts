import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "../api/client";

export interface AdminStats {
  movies: { total: number; published: number; draft: number };
  series: { total: number; published: number; draft: number };
  videos: { ready: number; processing: number; failed: number };
  users: { total: number; staff: number };
  subscriptions: { active: number };
}

export const useAdminStore = defineStore("admin", () => {
  const stats = ref<AdminStats | null>(null);
  const statsLoading = ref(false);

  async function loadStats() {
    statsLoading.value = true;
    try {
      const { data } = await api.get<AdminStats>("/admin/stats/");
      stats.value = data;
    } finally {
      statsLoading.value = false;
    }
  }

  return { stats, statsLoading, loadStats };
});
