"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";

interface DashboardHeaderProps {
  name: string;
  totalApplications: number;
  totalJobs: number;
  onRefresh?: () => void;
  refreshing?: boolean;
}

export function DashboardHeader({
  name,
  totalApplications,
  totalJobs,
  onRefresh,
  refreshing = false,
}: DashboardHeaderProps) {
  const t = useTranslations("Dashboard.home.header");
  const locale = useLocale();

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            {t("title", { name })}
          </h1>
          <p className="text-sm text-muted-foreground">{t("subtitle")}</p>
        </div>
        <div className="flex items-center gap-2">
          {onRefresh ? (
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              disabled={refreshing}
            >
              {refreshing ? t("actions.refreshing") : t("actions.refresh")}
            </Button>
          ) : null}
          <Button size="sm" asChild>
            <Link href={`/${locale}/dashboard/profile`}>
              {t("actions.profile")}
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border bg-background p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">
            {t("stats.applications.label")}
          </p>
          <p className="text-2xl font-semibold">{totalApplications}</p>
          <p className="text-xs text-muted-foreground">
            {t("stats.applications.caption")}
          </p>
        </div>
        <div className="rounded-lg border bg-background p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">
            {t("stats.jobs.label")}
          </p>
          <p className="text-2xl font-semibold">{totalJobs}</p>
          <p className="text-xs text-muted-foreground">
            {t("stats.jobs.caption")}
          </p>
        </div>
      </div>
    </div>
  );
}
