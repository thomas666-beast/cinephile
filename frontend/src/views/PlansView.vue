<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { useSubscriptionStore } from "../stores/subscription";

const { t } = useI18n();
const auth = useAuthStore();
const subs = useSubscriptionStore();
const router = useRouter();
const route = useRoute();

const error = ref<string | null>(null);
const subscribingSlug = ref<string | null>(null);

onMounted(async () => {
  await subs.loadPlans();
  if (auth.user) await subs.loadCurrent();
});

function formatPrice(priceCents: number): string {
  return (priceCents / 100).toFixed(2);
}

function periodLabel(p: "monthly" | "yearly"): string {
  return p === "monthly" ? t("subscription.periodMonthly") : t("subscription.periodYearly");
}

const currentPlanSlug = computed(() => subs.current?.plan.slug ?? null);

async function onSubscribe(slug: string) {
  error.value = null;
  if (!auth.user) {
    router.push({ name: "sign-in", query: { next: route.fullPath } });
    return;
  }
  subscribingSlug.value = slug;
  try {
    await subs.subscribe(slug);
    router.push({ name: "my-account" });
  } catch (e: any) {
    error.value = e?.response?.status === 409
      ? t("subscription.alreadySubscribed")
      : t("subscription.subscribeError");
  } finally {
    subscribingSlug.value = null;
  }
}
</script>

<template>
  <section class="max-w-4xl mx-auto px-6 py-16">
    <p class="label-caps mb-2">{{ t("nav.plans") }}</p>
    <h1 class="font-serif text-3xl md:text-4xl mb-2">{{ t("subscription.plansTitle") }}</h1>
    <p class="text-paper-300 mb-12 max-w-lg">{{ t("subscription.plansSubtitle") }}</p>

    <p v-if="subs.loadingPlans" class="label-caps">{{ t("common.loading") }}</p>
    <p v-else-if="error" class="text-blood-500 mb-6">{{ error }}</p>

    <ul v-else class="grid md:grid-cols-2 gap-5">
      <li
        v-for="plan in subs.plans"
        :key="plan.id"
        class="frame p-6 flex flex-col"
        :class="{ 'border-paper-100': currentPlanSlug === plan.slug }"
      >
        <p class="label-caps mb-3">
          {{ plan.name }}
          <span v-if="currentPlanSlug === plan.slug" class="ml-2 text-paper-100">
            · {{ t("subscription.currentPlan") }}
          </span>
        </p>

        <p class="font-serif text-4xl leading-none mb-1">
          {{ formatPrice(plan.price_cents) }}
          <span class="text-xl align-baseline">{{ plan.currency }}</span>
        </p>
        <p class="label-caps mb-6">/ {{ periodLabel(plan.billing_period) }}</p>

        <p v-if="plan.description" class="text-paper-300 text-sm mb-6">
          {{ plan.description }}
        </p>

        <div class="mt-auto">
          <button
            v-if="currentPlanSlug !== plan.slug"
            type="button"
            class="w-full bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps py-2.5 disabled:opacity-60"
            :disabled="subscribingSlug === plan.slug"
            @click="onSubscribe(plan.slug)"
          >
            {{ subscribingSlug === plan.slug ? t("common.loading") : t("subscription.subscribe") }}
          </button>
          <RouterLink
            v-else
            to="/my-account"
            class="block w-full text-center frame py-2.5 label-caps hover:border-paper-100"
          >
            {{ t("subscription.currentPlan") }}
          </RouterLink>
        </div>
      </li>
    </ul>

    <p v-if="!subs.loadingPlans && subs.plans.length === 0" class="label-caps mt-10">
      {{ t("common.noResults") }}
    </p>
  </section>
</template>
