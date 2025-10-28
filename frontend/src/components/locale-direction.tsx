"use client";

import { useLocale } from "next-intl";
import { useEffect } from "react";
import { isRtl, type Locale } from "@/i18n/config";

export default function LocaleDirection() {
  const locale = useLocale() as Locale;

  useEffect(() => {
    const direction = isRtl(locale) ? "rtl" : "ltr";
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
      document.documentElement.dir = direction;
    }
  }, [locale]);

  return null;
}
