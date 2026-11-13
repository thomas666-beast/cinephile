import { defineStore } from "pinia";
import { ref } from "vue";
import { authApi } from "../api";
import { tokenStore } from "../api/client";
import type { MeResponse } from "../api/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<MeResponse | null>(null);
  const loading = ref(false);

  async function hydrate() {
    if (!tokenStore.access && !tokenStore.refresh) return;
    loading.value = true;
    try {
      user.value = await authApi.me();
    } catch {
      user.value = null;
      tokenStore.clear();
    } finally {
      loading.value = false;
    }
  }

  async function login(email: string, password: string) {
    const tokens = await authApi.login({ email, password });
    tokenStore.set(tokens.access, tokens.refresh);
    user.value = await authApi.me();
  }

  async function register(body: { email: string; password: string; password_confirm: string;
                                  first_name?: string; last_name?: string }) {
    await authApi.register(body);
    await login(body.email, body.password);
  }

  async function logout() {
    const refresh = tokenStore.refresh;
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // best-effort — even if the server call fails, clear local tokens
    } finally {
      tokenStore.clear();
      user.value = null;
    }
  }

  return { user, loading, hydrate, login, register, logout };
});
