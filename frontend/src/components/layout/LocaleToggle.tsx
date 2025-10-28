"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "next/navigation";
import { useTransition } from "react";
import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Locale } from "@/i18n/config";

export default function LocaleToggle() {
  const locale = useLocale() as Locale;
  const t = useTranslations("Navigation");
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const targetLocale = locale === "en" ? "ar" : "en";
  const targetLocaleLabel = t(`localeNames.${targetLocale}`);

  const switchLocale = () => {
    startTransition(() => {
      const localeSegment = `/${locale}`;
      const pathWithoutLocale = pathname.startsWith(localeSegment)
        ? pathname.slice(localeSegment.length) || "/"
        : pathname || "/";
      const normalizedPath = pathWithoutLocale === "/" ? "/dashboard" : pathWithoutLocale;
      const nextPath = `/${targetLocale}${normalizedPath.startsWith("/") ? normalizedPath : `/${normalizedPath}`}`;
      router.replace(nextPath);
    });
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={switchLocale}
      disabled={isPending}
      className="flex items-center gap-2"
      aria-label={t("switchLocale", { locale: targetLocaleLabel })}
    >
      <Globe className="h-4 w-4" />
      <span className="font-medium uppercase">{targetLocale}</span>
    </Button>
  );
}
