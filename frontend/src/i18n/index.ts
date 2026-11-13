import { createI18n } from "vue-i18n";
import en from "./locales/en";

export const SUPPORTED_LOCALES = ["en"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export const LOCALE_LABELS: Record<SupportedLocale, string> = {
  en: "English",
};

/** Persisted choice, else browser preference, else English. */
function resolveInitialLocale(): SupportedLocale {
  const saved = localStorage.getItem("locale");
  if (saved && (SUPPORTED_LOCALES as readonly string[]).includes(saved)) {
    return saved as SupportedLocale;
  }
  const browser = navigator.language.split("-")[0];
  if ((SUPPORTED_LOCALES as readonly string[]).includes(browser)) {
    return browser as SupportedLocale;
  }
  return "en";
}

export const i18n = createI18n({
  legacy: false,        // Composition API mode
  locale: resolveInitialLocale(),
  fallbackLocale: "en",
  messages: {
    en,
  },
});

export function setLocale(locale: SupportedLocale) {
  i18n.global.locale.value = locale;
  localStorage.setItem("locale", locale);
  document.documentElement.setAttribute("lang", locale);
}
