"use client";

import { useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { NotificationBell } from "@/components/layout/NotificationBell";
import { useAuth } from "@/lib/store";
import { cn } from "@/lib/utils";

export function Topbar() {
  const router = useRouter();
  const locale = useLocale();
  const pathname = usePathname();
  const t = useTranslations("Navigation");
  const queryClient = useQueryClient();
  const { logout, user } = useAuth();
  const nextLocale = locale === "en" ? "ar" : "en";
  const nextLocaleLabel = t(`localeNames.${nextLocale}`);

  const handleLogout = useCallback(() => {
    logout();
    queryClient.clear();
    router.replace(`/${locale}/login`);
  }, [locale, logout, queryClient, router]);

  const handleLocaleSwitch = useCallback(() => {
    const localeSegment = `/${locale}`;
    const trimmedPath = pathname.startsWith(localeSegment)
      ? pathname.slice(localeSegment.length) || "/dashboard"
      : "/dashboard";
    const normalizedPath = trimmedPath.startsWith("/") ? trimmedPath : `/${trimmedPath}`;
    router.push(`/${nextLocale}${normalizedPath}`);
  }, [locale, nextLocale, pathname, router]);

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-background/80 px-4 shadow-sm sm:px-6">
      <div className="flex flex-col">
        <span className="text-xs uppercase tracking-wide text-muted-foreground">{t("account")}</span>
        <span className="font-semibold">{user?.full_name ?? user?.email ?? t("guest")}</span>
      </div>
      <div className={cn("flex items-center gap-2", locale === "ar" && "flex-row-reverse")}
      >
        <NotificationBell />
        <Button
          variant="outline"
          size="sm"
          onClick={handleLocaleSwitch}
          aria-label={t("switchLocale", { locale: nextLocaleLabel })}
        >
          {nextLocale.toUpperCase()}
        </Button>
        <Button
          variant="destructive"
          size="sm"
          onClick={handleLogout}
          aria-label={t("logoutAria")}
        >
          {t("logout")}
        </Button>
      </div>
    </header>
  );
}
