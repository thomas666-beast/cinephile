<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import { isValidEmail, minLength } from "../lib/validate";

const { t } = useI18n();
const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  email: "",
  password: "",
  password_confirm: "",
  first_name: "",
  last_name: "",
});

const errors = reactive<Record<string, string>>({});
const serverError = ref<string | null>(null);
const submitting = ref(false);

function validate(): boolean {
  Object.keys(errors).forEach(k => (errors[k] = ""));
  let ok = true;

  if (!form.email.trim()) {
    errors.email = t("auth.emailRequired");
    ok = false;
  } else if (!isValidEmail(form.email)) {
    errors.email = t("auth.emailInvalid");
    ok = false;
  }
  if (!form.password) {
    errors.password = t("auth.passwordRequired");
    ok = false;
  } else if (!minLength(form.password, 8)) {
    errors.password = t("auth.passwordTooShort");
    ok = false;
  }
  if (form.password !== form.password_confirm) {
    errors.password_confirm = t("auth.passwordMismatch");
    ok = false;
  }
  return ok;
}

async function onSubmit() {
  serverError.value = null;
  if (!validate()) return;
  submitting.value = true;
  try {
    await auth.register({
      email: form.email.trim(),
      password: form.password,
      password_confirm: form.password_confirm,
      first_name: form.first_name.trim() || undefined,
      last_name: form.last_name.trim() || undefined,
    });
    router.push("/");
  } catch (e: any) {
    if (e?.response?.status === 400) {
      const detail = e.response.data;
      // Handle DRF field-level errors if present.
      if (detail && typeof detail === "object") {
        for (const [key, value] of Object.entries(detail)) {
          const msg = Array.isArray(value) ? value[0] : String(value);
          if (key in errors) {
            errors[key] = msg;
          } else {
            serverError.value = msg;
          }
        }
      }
      if (!serverError.value && detail?.email) {
        serverError.value = t("auth.emailTaken");
      }
    } else {
      serverError.value = t("auth.genericError");
    }
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <section class="max-w-md mx-auto px-6 py-24">
    <p class="label-caps mb-3">{{ t("nav.register") }}</p>
    <h1 class="font-serif text-4xl mb-3">{{ t("auth.registerTitle") }}</h1>
    <p class="text-paper-300 mb-12">{{ t("auth.registerSubtitle") }}</p>

    <form novalidate @submit.prevent="onSubmit" class="space-y-6">
      <div>
        <label for="email" class="label-caps block mb-2">{{ t("auth.email") }}</label>
        <input id="email" v-model="form.email" type="email" autocomplete="email"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-3 text-paper-100 outline-none"
          :class="{ 'border-blood-500': errors.email }" />
        <p v-if="errors.email" class="mt-2 text-sm text-blood-500">{{ errors.email }}</p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="first_name" class="label-caps block mb-2">{{ t("auth.firstName") }}</label>
          <input id="first_name" v-model="form.first_name" type="text" autocomplete="given-name"
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-3 text-paper-100 outline-none" />
        </div>
        <div>
          <label for="last_name" class="label-caps block mb-2">{{ t("auth.lastName") }}</label>
          <input id="last_name" v-model="form.last_name" type="text" autocomplete="family-name"
            class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-3 text-paper-100 outline-none" />
        </div>
      </div>

      <div>
        <label for="password" class="label-caps block mb-2">{{ t("auth.password") }}</label>
        <input id="password" v-model="form.password" type="password" autocomplete="new-password"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-3 text-paper-100 outline-none"
          :class="{ 'border-blood-500': errors.password }" />
        <p v-if="errors.password" class="mt-2 text-sm text-blood-500">{{ errors.password }}</p>
      </div>

      <div>
        <label for="password_confirm" class="label-caps block mb-2">{{ t("auth.confirmPassword") }}</label>
        <input id="password_confirm" v-model="form.password_confirm" type="password" autocomplete="new-password"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-4 py-3 text-paper-100 outline-none"
          :class="{ 'border-blood-500': errors.password_confirm }" />
        <p v-if="errors.password_confirm" class="mt-2 text-sm text-blood-500">{{ errors.password_confirm }}</p>
      </div>

      <p v-if="serverError" class="text-sm text-blood-500">{{ serverError }}</p>

      <button type="submit"
        class="w-full bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps py-4 disabled:opacity-60"
        :disabled="submitting">
        {{ submitting ? t("auth.creatingAccount") : t("auth.registerCta") }}
      </button>
    </form>

    <p class="mt-12 label-caps">
      {{ t("auth.signInLinkPrompt") }}
      <RouterLink to="/sign-in" class="ml-2 text-paper-100 border-b border-blood-500 pb-0.5">
        {{ t("nav.signIn") }}
      </RouterLink>
    </p>
  </section>
</template>
