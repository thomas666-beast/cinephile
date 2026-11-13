<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { passwordApi } from "../api";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const uid = computed(() => String(route.query.uid ?? ""));
const token = computed(() => String(route.query.token ?? ""));

const form = reactive({ new_password: "", confirm_password: "" });
const errors = reactive<Record<string, string>>({});
const submitting = ref(false);
const success = ref(false);
const serverError = ref<string | null>(null);

function validate(): boolean {
  Object.keys(errors).forEach(k => (errors[k] = ""));
  let ok = true;
  if (form.new_password.length < 8) {
    errors.new_password = t("auth.passwordTooShort");
    ok = false;
  }
  if (form.new_password !== form.confirm_password) {
    errors.confirm_password = t("auth.passwordMismatch");
    ok = false;
  }
  return ok;
}

async function onSubmit() {
  serverError.value = null;
  if (!validate()) return;
  submitting.value = true;
  try {
    await passwordApi.confirmReset({
      uid: uid.value,
      token: token.value,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    });
    success.value = true;
    setTimeout(() => router.push("/sign-in"), 2500);
  } catch (e: any) {
    const detail = e?.response?.data?.detail;
    if (Array.isArray(detail)) serverError.value = detail[0];
    else if (typeof detail === "string") serverError.value = detail;
    else serverError.value = t("auth.genericError");
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <section class="max-w-xl mx-auto px-6 py-16">
    <p class="label-caps mb-2">{{ t("nav.signIn") }}</p>
    <h1 class="font-serif text-3xl mb-2">{{ t("passwordReset.confirmTitle") }}</h1>
    <p class="text-paper-300 text-sm mb-10">{{ t("passwordReset.confirmSubtitle") }}</p>

    <div v-if="success" class="frame p-6">
      <p class="label-caps mb-3">{{ t("passwordReset.confirmSuccess") }}</p>
      <RouterLink to="/sign-in" class="text-paper-100 border-b border-blood-500 pb-0.5 label-caps">
        {{ t("nav.signIn") }}
      </RouterLink>
    </div>

    <form v-else novalidate class="space-y-5" @submit.prevent="onSubmit">
      <div>
        <label for="new_password" class="label-caps block mb-2">{{ t("passwordReset.newPassword") }}</label>
        <input
          id="new_password" v-model="form.new_password" type="password" autocomplete="new-password"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none"
          :class="{ 'border-blood-500': errors.new_password }"
        />
        <p v-if="errors.new_password" class="mt-2 text-sm text-blood-500">{{ errors.new_password }}</p>
      </div>

      <div>
        <label for="confirm_password" class="label-caps block mb-2">{{ t("passwordReset.confirmPassword") }}</label>
        <input
          id="confirm_password" v-model="form.confirm_password" type="password" autocomplete="new-password"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none"
          :class="{ 'border-blood-500': errors.confirm_password }"
        />
        <p v-if="errors.confirm_password" class="mt-2 text-sm text-blood-500">{{ errors.confirm_password }}</p>
      </div>

      <p v-if="serverError" class="text-sm text-blood-500">{{ serverError }}</p>

      <button
        type="submit"
        class="w-full bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps py-2.5 disabled:opacity-60"
        :disabled="submitting"
      >
        {{ submitting ? t("common.loading") : t("passwordReset.confirmCta") }}
      </button>
    </form>
  </section>
</template>
