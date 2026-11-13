import type { Router } from "vue-router";
import { useAuthStore } from "../stores/auth";

export function installGuards(router: Router) {
  router.beforeEach(async (to) => {
    if (!to.path.startsWith("/admin")) return true;

    const auth = useAuthStore();

    // Try to hydrate if we haven't yet (in case the user landed directly on /admin)
    if (!auth.user) {
      await auth.hydrate();
    }

    if (!auth.user) {
      return { name: "sign-in", query: { next: to.fullPath } };
    }
    if (!auth.user.is_staff) {
      return { name: "home" };
    }
    return true;
  });
}
