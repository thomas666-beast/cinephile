import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api } from "../api/client";

export interface Profile {
  id: number;
  name: string;
  is_kids: boolean;
  initial: string;
  created_at: string;
}

const ACTIVE_KEY = "cinephile.activeProfile";

export const useProfileStore = defineStore("profiles", () => {
  const profiles = ref<Profile[]>([]);
  const activeId = ref<number | null>(
    Number(localStorage.getItem(ACTIVE_KEY)) || null,
  );
  const loading = ref(false);

  const active = computed<Profile | null>(
    () => profiles.value.find(p => p.id === activeId.value) ?? null,
  );

  async function load() {
    loading.value = true;
    try {
      const { data } = await api.get<Profile[]>("/profiles/");
      profiles.value = data;
      if (activeId.value && !data.some(p => p.id === activeId.value)) {
        activeId.value = null;
        localStorage.removeItem(ACTIVE_KEY);
      }
    } finally {
      loading.value = false;
    }
  }

  function setActive(id: number) {
    activeId.value = id;
    localStorage.setItem(ACTIVE_KEY, String(id));
  }

  async function create(name: string, isKids = false) {
    const { data } = await api.post<Profile>("/profiles/", { name, is_kids: isKids });
    profiles.value.push(data);
    return data;
  }

  async function remove(id: number) {
    await api.delete(`/profiles/${id}/`);
    profiles.value = profiles.value.filter(p => p.id !== id);
    if (activeId.value === id) {
      activeId.value = profiles.value[0]?.id ?? null;
      if (activeId.value) localStorage.setItem(ACTIVE_KEY, String(activeId.value));
      else localStorage.removeItem(ACTIVE_KEY);
    }
  }

  return { profiles, activeId, active, loading, load, setActive, create, remove };
});
