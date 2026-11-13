<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { useSubscriptionStore } from "../stores/subscription";

const { t } = useI18n();
const auth = useAuthStore();
const subs = useSubscriptionStore();
const router = useRouter();

const error = ref<string | null>(null);
const canceling = ref(false);
const showCancelConfirm = ref(false);

onMounted(async () => {
  if (!auth.user) {
    router.push({ name: "sign-in", query: { next: "/my-account" } });
    return;
  }
  await subs.loadCurrent();
});

const formattedExpiry = computed(() => {
  if (!subs.current) return null;
  const d = new Date(subs.current.expires_at);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
});

async function onCancel() {
  error.value = null;
  canceling.value = true;
  try {
    await subs.cancel();
    showCancelConfirm.value = false;
  } catch {
    error.value = t("subscription.cancelError");
  } finally {
    canceling.value = false;
  }
}
</script>

<template>
  <section class="max-w-2xl mx-auto px-6 py-16">
    <p class="label-caps mb-2">{{ t("nav.myAccount") }}</p>
    <h1 class="font-serif text-3xl md:text-4xl mb-2">{{ t("subscription.myAccountTitle") }}</h1>
    <p class="text-paper-300 mb-12">{{ t("subscription.myAccountSubtitle") }}</p>

    <section>
      <h2 class="label-caps mb-4">{{ t("subscription.subscriptionSection") }}</h2>

      <p v-if="subs.loadingCurrent" class="label-caps">{{ t("common.loading") }}</p>

      <div v-else-if="subs.current" class="frame p-6">
        <p class="label-caps mb-2">{{ t("subscription.currentPlan") }}</p>
        <p class="font-serif text-2xl mb-1">{{ subs.current.plan.name }}</p>
        <p class="text-paper-300 text-sm mb-6">
          {{ t("subscription.activeUntil", { date: formattedExpiry }) }}
        </p>

        <div v-if="!showCancelConfirm">
          <button
            type="button"
            class="frame px-4 py-2 label-caps hover:border-blood-500 hover:text-blood-500 transition-colors"
            :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
            @click="showCancelConfirm = true"
          >
            {{ t("subscription.cancel") }}
          </button>
        </div>

        <div v-else class="border-t border-paper-300/20 pt-5">
          <p class="font-serif text-lg mb-2">{{ t("subscription.cancelConfirmTitle") }}</p>
          <p class="text-paper-300 text-sm mb-5">{{ t("subscription.cancelConfirmBody") }}</p>
          <p v-if="error" class="text-blood-500 text-sm mb-3">{{ error }}</p>
          <div class="flex gap-2">
            <button
              type="button"
              class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-4 py-2 disabled:opacity-60"
              :disabled="canceling"
              @click="onCancel"
            >
              {{ canceling ? t("common.loading") : t("subscription.cancelConfirmDo") }}
            </button>
            <button
              type="button"
              class="frame px-4 py-2 label-caps hover:border-paper-100"
              :disabled="canceling"
              @click="showCancelConfirm = false"
            >
              {{ t("subscription.cancelConfirmKeep") }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="frame p-6">
        <p class="label-caps mb-2">{{ t("subscription.noActiveSubscription") }}</p>
        <p class="text-paper-300 text-sm mb-5">{{ t("subscription.notSubscribedDescription") }}</p>
        <RouterLink
          to="/plans"
          class="inline-block bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-4 py-2"
        >
          {{ t("subscription.choosePlan") }}
        </RouterLink>
      </div>
    </section>
  </section>
</template>
