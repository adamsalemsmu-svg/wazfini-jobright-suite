"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, User } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

const navItems = [
  {
    href: "/dashboard",
    icon: Home,
    translationKey: "nav.home",
  },
  {
    href: "/dashboard/profile",
    icon: User,
    translationKey: "nav.profile",
  },
] as const;

export function Sidebar() {
  const locale = useLocale();
  const t = useTranslations("Dashboard");
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "hidden w-64 shrink-0 border-r border-border bg-background/80 px-6 py-8 shadow-sm md:flex md:flex-col",
        locale === "ar" && "border-l border-r-0"
      )}
      dir={locale === "ar" ? "rtl" : "ltr"}
      aria-label={t("navLabel")}
    >
      <div className="text-lg font-semibold" aria-label={t("brand")}>
        {t("brand")}
      </div>
      <nav className="mt-8 flex flex-1 flex-col gap-2 text-sm font-medium" aria-label={t("navLabel")}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const href = `/${locale}${item.href}`;
          const isActive = pathname.startsWith(href);

          return (
            <Link
              key={item.href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 transition-colors",
                locale === "ar" && "flex-row-reverse text-right",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
              )}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className="h-4 w-4" />
              <span>{t(item.translationKey)}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
