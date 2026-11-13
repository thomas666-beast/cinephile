<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useSubscriptionStore } from "../../stores/subscription";
import AdminPageHeader from "../../components/admin/AdminPageHeader.vue";
import AdminPrimaryButton from "../../components/admin/AdminPrimaryButton.vue";

const { t } = useI18n();
const subs = useSubscriptionStore();

const loading = ref(true);
const saving = ref(false);
const serverError = ref<string | null>(null);

const form = reactive({
  name: "",
  description: "",
  price_cents: 999,
  duration_days: 30,
  billing_period: "monthly" as "monthly" | "yearly",
  currency: "USD",
});

async function load() {
  loading.value = true;
  try {
    await subs.loadPlans();
  } finally {
    loading.value = false;
  }
}

async function onCreate() {
  serverError.value = null;
  saving.value = true;
  try {
    const { api } = await import("../../api/client");
    await api.post("/admin/plans/", form);
    form.name = "";
    form.description = "";
    await load();
  } catch (e: any) {
    serverError.value = e?.response?.data?.detail ?? t("common.error");
  } finally {
    saving.value = false;
  }
}

async function onDelete(slug: string) {
  if (!confirm(t("admin.confirmDeleteBody"))) return;
  const { api } = await import("../../api/client");
  await api.delete(`/admin/plans/${slug}/`);
  await load();
}

onMounted(load);
</script>

<template>
  <div>
    <AdminPageHeader :label="t('admin.navSection')" :title="t('admin.listPlansTitle')" />

    <div class="border border-paper-300/20">
      <table class="w-full text-left text-sm">
        <thead class="bg-noir-900 border-b border-paper-300/20">
          <tr>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colName") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colPrice") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300">{{ t("admin.colPeriod") }}</th>
            <th class="label-caps px-4 py-2 font-normal text-paper-300 text-right">{{ t("admin.colActions") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="4" class="px-4 py-12 text-center label-caps text-paper-300/60">{{ t("common.loading") }}</td>
          </tr>
          <tr v-else-if="subs.plans.length === 0">
            <td colspan="4" class="px-4 py-12 text-center label-caps text-paper-300/60">{{ t("admin.noRows") }}</td>
          </tr>
          <tr
            v-for="plan in subs.plans"
            :key="plan.id"
            class="border-b border-paper-300/10 last:border-b-0 hover:bg-noir-800/40 transition-colors"
          >
            <td class="px-4 py-2 text-paper-100">{{ plan.name }}</td>
            <td class="px-4 py-2 text-paper-300">{{ (plan.price_cents / 100).toFixed(2) }} {{ plan.currency }}</td>
            <td class="px-4 py-2 text-paper-300">{{ plan.billing_period }}</td>
            <td class="px-4 py-2 text-right">
              <button type="button" class="text-paper-300 hover:text-blood-500 label-caps text-xs" @click="onDelete(plan.slug)">
                {{ t("admin.delete") }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-8 border border-paper-300/20 p-4">
      <p class="label-caps mb-4">{{ t("admin.newPlan") ?? "New plan" }}</p>
      <form class="grid grid-cols-2 gap-3" @submit.prevent="onCreate">
        <input v-model="form.name" placeholder="Name" required class="bg-transparent border border-paper-300/30 px-3 py-1.5 text-sm text-paper-100 outline-none" />
        <input v-model.number="form.price_cents" type="number" placeholder="Price (cents)" required class="bg-transparent border border-paper-300/30 px-3 py-1.5 text-sm text-paper-100 outline-none" />
        <input v-model.number="form.duration_days" type="number" placeholder="Duration (days)" required class="bg-transparent border border-paper-300/30 px-3 py-1.5 text-sm text-paper-100 outline-none" />
        <select v-model="form.billing_period" class="bg-transparent border border-paper-300/30 px-3 py-1.5 text-sm text-paper-100 outline-none">
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
        <input v-model="form.description" placeholder="Description" class="col-span-2 bg-transparent border border-paper-300/30 px-3 py-1.5 text-sm text-paper-100 outline-none" />
        <p v-if="serverError" class="col-span-2 text-blood-500 text-sm">{{ serverError }}</p>
        <div class="col-span-2">
          <AdminPrimaryButton type="submit" :disabled="saving">
            {{ saving ? t("admin.saving") : t("admin.create") ?? "Create" }}
          </AdminPrimaryButton>
        </div>
      </form>
    </div>
  </div>
</template>
