import { getRequestConfig } from "next-intl/server";
import { defaultLocale, locales, type Locale } from "@/i18n/config";
import { getMessages } from "@/i18n/getMessages";

export default getRequestConfig(async ({ locale }) => {
  const resolved = (locale ?? defaultLocale) as Locale;
  const safeLocale = locales.includes(resolved) ? resolved : defaultLocale;

  return {
    locale: safeLocale,
    messages: await getMessages(safeLocale),
  };
});
