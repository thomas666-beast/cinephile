import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import { router } from "./router";
import { i18n, setLocale } from "./i18n";
import "./styles/main.css";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(i18n);

// Sync the html lang attribute with the initial locale
setLocale(i18n.global.locale.value as never);

// Hydrate auth from existing tokens (if present) — non-blocking
import { useAuthStore } from "./stores/auth";
useAuthStore().hydrate();

app.mount("#app");
