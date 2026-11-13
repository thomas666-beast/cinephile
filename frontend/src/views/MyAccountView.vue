<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { useSubscriptionStore } from "../stores/subscription";
import { useProfileStore } from "../stores/profiles";

const { t } = useI18n();
const auth = useAuthStore();
const subs = useSubscriptionStore();
const profiles = useProfileStore();
const router = useRouter();

const error = ref<string | null>(null);
const canceling = ref(false);
const showCancelConfirm = ref(false);
const newProfileName = ref("");
const profileError = ref<string | null>(null);

onMounted(async () => {
  if (!auth.user) {
    router.push({ name: "sign-in", query: { next: "/my-account" } });
    return;
  }
  await subs.loadCurrent();
  await profiles.load();
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

async function addProfile() {
  profileError.value = null;
  const name = newProfileName.value.trim();
  if (!name) return;
  try {
    await profiles.create(name);
    newProfileName.value = "";
  } catch (e: any) {
    const detail = e?.response?.data;
    if (typeof detail === "object" && detail !== null) {
      const first = Object.values(detail)[0];
      profileError.value = Array.isArray(first) ? first[0] : String(first);
    } else {
      profileError.value = t("common.error");
    }
  }
}
</script>

<template>
  <section class="max-w-2xl mx-auto px-6 py-16">
    <p class="label-caps mb-2">{{ t("nav.myAccount") }}</p>
    <h1 class="font-serif text-3xl md:text-4xl mb-2">{{ t("subscription.myAccountTitle") }}</h1>
    <p class="text-paper-300 mb-12">{{ t("subscription.myAccountSubtitle") }}</p>

    <!-- Subscription Section -->
    <section>
      <h2 class="label-caps mb-4">{{ t("subscription.subscriptionSection") }}</h2>

      <p v-if="subs.loadingCurrent" class="label-caps">{{ t("common.loading") }}</p>

      <template v-else>
        <!-- Active subscription -->
        <div v-if="subs.current" class="frame p-6">
          <p class="label-caps mb-2">{{ t("subscription.currentPlan") }}</p>
          <p class="font-serif text-2xl mb-1">{{ subs.current.plan.name }}</p>
          <p class="text-paper-300 text-sm mb-6">
            {{ t("subscription.activeUntil", { date: formattedExpiry }) }}
          </p>

          <button
            type="button"
            class="frame px-4 py-2 label-caps hover:border-blood-500 hover:text-blood-500 transition-colors"
            :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
            @click="showCancelConfirm = true"
          >
            {{ t("subscription.cancel") }}
          </button>
        </div>

        <!-- No subscription -->
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
      </template>
    </section>

    <!-- Profiles Section -->
    <section class="mt-12">
      <h2 class="label-caps mb-4">{{ t("profiles.sectionTitle") }}</h2>

      <ul class="frame divide-y divide-paper-300/15">
        <li v-if="profiles.loading" class="px-5 py-6 text-center label-caps">
          {{ t("common.loading") }}
        </li>
        <li v-else-if="profiles.profiles.length === 0" class="px-5 py-6 text-center label-caps">
          {{ t("admin.noRows") }}
        </li>
        <li
          v-for="p in profiles.profiles"
          :key="p.id"
          class="px-5 py-3 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <span class="w-6 h-6 frame flex items-center justify-center font-serif text-xs">
              {{ p.initial }}
            </span>
            <span class="font-serif text-base">{{ p.name }}</span>
            <span v-if="p.is_kids" class="label-caps text-paper-300">· {{ t("profiles.kids") }}</span>
          </div>
          <button
            type="button"
            class="label-caps hover:text-blood-500"
            @click="profiles.remove(p.id)"
          >
            {{ t("admin.delete") }}
          </button>
        </li>
      </ul>

      <form class="flex gap-2 mt-4" @submit.prevent="addProfile">
        <input
          v-model="newProfileName"
          type="text"
          :placeholder="t('profiles.newPlaceholder')"
          class="flex-1 bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none"
        />
        <button
          type="submit"
          class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-4 py-2"
        >
          {{ t("profiles.add") }}
        </button>
      </form>
      <p v-if="profileError" class="mt-2 text-sm text-blood-500">{{ profileError }}</p>
    </section>

    <!-- Cancel Confirmation Modal -->
    <Teleport to="body">
      <div
        v-if="showCancelConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      >
        <div class="frame bg-noir-950 p-8 max-w-md w-full">
          <p class="label-caps mb-2 text-blood-500">{{ t("subscription.cancel") }}</p>
          <p class="font-serif text-2xl mb-4">{{ t("subscription.cancelConfirmTitle") }}</p>
          <p class="text-paper-300 text-sm mb-8">{{ t("subscription.cancelConfirmBody") }}</p>

          <p v-if="error" class="text-blood-500 text-sm mb-4">{{ error }}</p>

          <div class="flex gap-3 justify-end">
            <button
              type="button"
              class="frame px-4 py-2 label-caps hover:border-paper-100"
              :disabled="canceling"
              @click="showCancelConfirm = false"
            >
              {{ t("subscription.cancelConfirmKeep") }}
            </button>
            <button
              type="button"
              class="bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps px-4 py-2 disabled:opacity-60"
              :disabled="canceling"
              @click="onCancel"
            >
              {{ canceling ? t("common.loading") : t("subscription.cancelConfirmDo") }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>
