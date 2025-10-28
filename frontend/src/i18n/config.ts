export const locales = ["en", "ar"] as const;

export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "en";

export function isRtl(locale: Locale): boolean {
  return locale === "ar";
}
