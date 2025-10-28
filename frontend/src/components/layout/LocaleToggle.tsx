"use client";

import { useLocale } from "next-intl";
import { usePathname, useRouter } from "next/navigation";
import { useTransition } from "react";
import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Locale } from "@/i18n/config";

export default function LocaleToggle() {
  const locale = useLocale() as Locale;
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const targetLocale = locale === "en" ? "ar" : "en";

  const switchLocale = () => {
    startTransition(() => {
      const localeSegment = `/${locale}`;
      const pathWithoutLocale = pathname.startsWith(localeSegment)
        ? pathname.replace(localeSegment, "") || "/"
        : pathname;
      const nextPath = `/${targetLocale}${pathWithoutLocale}`;
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
    >
      <Globe className="h-4 w-4" />
      <span className="font-medium uppercase">{targetLocale}</span>
    </Button>
  );
}
