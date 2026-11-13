<script setup lang="ts">
import { reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { useI18n } from "vue-i18n";
import { passwordApi } from "../api";
import { isValidEmail } from "../lib/validate";

const { t } = useI18n();
const form = reactive({ email: "" });
const errors = reactive<Record<string, string>>({});
const submitting = ref(false);
const done = ref(false);
const serverError = ref<string | null>(null);

function validate(): boolean {
  errors.email = "";
  if (!form.email.trim()) { errors.email = t("auth.emailRequired"); return false; }
  if (!isValidEmail(form.email)) { errors.email = t("auth.emailInvalid"); return false; }
  return true;
}

async function onSubmit() {
  serverError.value = null;
  if (!validate()) return;
  submitting.value = true;
  try {
    await passwordApi.requestReset(form.email.trim());
    done.value = true;
  } catch {
    serverError.value = t("auth.genericError");
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <section class="max-w-xl mx-auto px-6 py-16">
    <p class="label-caps mb-2">{{ t("nav.signIn") }}</p>
    <h1 class="font-serif text-3xl mb-2">{{ t("passwordReset.requestTitle") }}</h1>
    <p class="text-paper-300 text-sm mb-10">{{ t("passwordReset.requestSubtitle") }}</p>

    <div v-if="done" class="frame p-6">
      <p class="label-caps">{{ t("passwordReset.requestSuccess") }}</p>
    </div>

    <form v-else novalidate class="space-y-5" @submit.prevent="onSubmit">
      <div>
        <label for="email" class="label-caps block mb-2">{{ t("auth.email") }}</label>
        <input
          id="email" v-model="form.email" type="email" autocomplete="email"
          class="w-full bg-transparent border border-paper-300/40 focus:border-paper-100 px-3 py-2 text-paper-100 outline-none"
          :class="{ 'border-blood-500': errors.email }"
        />
        <p v-if="errors.email" class="mt-2 text-sm text-blood-500">{{ errors.email }}</p>
      </div>

      <p v-if="serverError" class="text-sm text-blood-500">{{ serverError }}</p>

      <button
        type="submit"
        class="w-full bg-blood-500 hover:bg-blood-700 text-paper-100 label-caps py-2.5 disabled:opacity-60"
        :disabled="submitting"
      >
        {{ submitting ? t("common.loading") : t("passwordReset.requestCta") }}
      </button>
    </form>

    <p class="mt-10 label-caps text-paper-300">
      <RouterLink to="/sign-in" class="text-paper-100 border-b border-blood-500 pb-0.5 whitespace-nowrap">
        {{ t("nav.signIn") }}
      </RouterLink>
    </p>
  </section>
</template>
