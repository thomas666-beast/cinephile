import { defineStore } from "pinia";
import { ref } from "vue";
import { subscriptionApi } from "../api";
import type { SubscriptionPlan, SubscriptionResponse } from "../api/types";

export const useSubscriptionStore = defineStore("subscription", () => {
  const plans = ref<SubscriptionPlan[]>([]);
  const current = ref<SubscriptionResponse | null>(null);
  const loadingPlans = ref(false);
  const loadingCurrent = ref(false);

  async function loadPlans() {
    loadingPlans.value = true;
    try {
      plans.value = await subscriptionApi.plans();
    } finally {
      loadingPlans.value = false;
    }
  }

  async function loadCurrent() {
    loadingCurrent.value = true;
    try {
      current.value = await subscriptionApi.me();
    } catch (e: any) {
      if (e?.response?.status === 404) {
        current.value = null;
      } else {
        // Surface unexpected errors — but don't crash the account page.
        current.value = null;
      }
    } finally {
      loadingCurrent.value = false;
    }
  }

  async function subscribe(planSlug: string) {
    current.value = await subscriptionApi.subscribe(planSlug);
  }

  async function cancel() {
    if (!current.value) return;
    current.value = await subscriptionApi.cancel(current.value.id);
  }

  function clear() {
    current.value = null;
    plans.value = [];
  }

  return { plans, current, loadingPlans, loadingCurrent, loadPlans, loadCurrent, subscribe, cancel, clear };
});
