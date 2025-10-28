"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/store";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const locale = useLocale();
  const { token } = useAuth();

  useEffect(() => {
    if (!token) {
      router.replace(`/${locale}/login`);
    }
  }, [locale, router, token]);

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/10">
        <p className="text-sm text-muted-foreground">Redirecting…</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex min-h-screen bg-muted/10 text-foreground transition-colors",
        locale === "ar" && "flex-row-reverse"
      )}
      dir={locale === "ar" ? "rtl" : "ltr"}
    >
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 py-6">
          <div className="container flex-1 space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
