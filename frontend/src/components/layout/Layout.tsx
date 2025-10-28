"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { ReactNode } from "react";
import { Home, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import LocaleToggle from "@/components/layout/LocaleToggle";
import { useAuth } from "@/lib/store";
import { cn } from "@/lib/utils";

const navItems = [
  {
    href: "/dashboard",
    icon: Home,
    translationKey: "Navigation.dashboard",
  },
];

export default function LayoutShell({ children }: { children: ReactNode }) {
  const t = useTranslations();
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const locale = useLocale();

  const localePrefix = `/${locale}`;

  const handleLogout = () => {
    logout();
    router.replace(`${localePrefix}/login`);
  };

  return (
    <div className="flex min-h-screen bg-muted/10">
      <aside className="hidden w-64 flex-col border-r bg-background/80 px-6 py-8 md:flex">
        <div className="text-xl font-semibold">Wazifni</div>
        <nav className="mt-8 flex flex-col gap-2 text-sm font-medium">
          {navItems.map((item) => {
            const href = `${localePrefix}${item.href}`;
            const isActive = pathname.startsWith(href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{t(item.translationKey)}</span>
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto flex flex-col gap-3">
          <LocaleToggle />
          <Button variant="outline" className="justify-start gap-2" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
            {t("Navigation.logout")}
          </Button>
        </div>
      </aside>
      <div className="flex flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b bg-background/80 px-4 shadow-sm">
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">{t("Navigation.account")}</span>
            <span className="font-semibold">
              {user?.full_name ?? user?.email ?? t("Navigation.guest")}
            </span>
          </div>
          <div className="flex items-center gap-3 md:hidden">
            <LocaleToggle />
            <Button variant="outline" size="sm" onClick={handleLogout}>
              {t("Navigation.logout")}
            </Button>
          </div>
        </header>
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
