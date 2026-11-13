<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { isValidEmail } from "../lib/validate";

const { t } = useI18n();
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const form = reactive({ email: "", password: "" });
const errors = reactive<Record<string, string>>({});
const serverError = ref<string | null>(null);
const submitting = ref(false);

function validate(): boolean {
  errors.email = "";
  errors.password = "";
  let ok = true;
  if (!form.email.trim()) { errors.email = t("auth.emailRequired"); ok = false; }
  else if (!isValidEmail(form.email)) { errors.email = t("auth.emailInvalid"); ok = false; }
  if (!form.password) { errors.password = t("auth.passwordRequired"); ok = false; }
  return ok;
}

async function onSubmit() {
  serverError.value = null;
  if (!validate()) return;
  submitting.value = true;
  try {
    await auth.login(form.email.trim(), form.password);
    const next = typeof route.query.next === "string" ? route.query.next : "/";
    router.push(next);
  } catch (e: any) {
    serverError.value = e?.response?.status === 401
      ? t("auth.invalidCredentials")
      : t("auth.genericError");
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <section class="max-w-sm mx-auto px-6 py-16">
    <p class="label-caps mb-2">{{ t("nav.signIn") }}</p>
    <h1 class="font-serif text-3xl mb-2">{{ t("auth.signInTitle") }}</h1>
    <p class="text-paper-300 text-sm mb-10">{{ t("auth.signInSubtitle") }}</p>

    <form novalidate class="space-y-5" @submit.prevent="onSubmit">
      <div>
        <label for="email" class="label-caps block mb-2">{{ t("auth.email") }}</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          autocomplete="email"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none transition-colors"
          :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
          :class="{ 'border-blood-500': errors.email }"
        />
        <p v-if="errors.email" class="mt-2 text-sm text-blood-500">{{ errors.email }}</p>
      </div>

      <div>
        <label for="password" class="label-caps block mb-2">{{ t("auth.password") }}</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          autocomplete="current-password"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none transition-colors"
          :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
          :class="{ 'border-blood-500': errors.password }"
        />
        <p v-if="errors.password" class="mt-2 text-sm text-blood-500">{{ errors.password }}</p>
      </div>

      <p v-if="serverError" class="text-sm text-blood-500">{{ serverError }}</p>

      <button
        type="submit"
        class="w-full bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps py-2.5 disabled:opacity-60 transition-colors"
        :style="{ transitionDuration: 'var(--duration-quick)', transitionTimingFunction: 'var(--ease-hitchcock)' }"
        :disabled="submitting"
      >
        {{ submitting ? t("auth.signingIn") : t("auth.signInCta") }}
      </button>
    </form>

    <p class="mt-10 label-caps">
      {{ t("auth.registerLinkPrompt") }}
      <RouterLink to="/register" class="ml-2 text-paper-100 border-b border-blood-500 pb-0.5">
        {{ t("nav.register") }}
      </RouterLink>
    </p>
  </section>
</template>
