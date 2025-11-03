"use client";

import { useLocale, useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ApplicationSummary } from "@/hooks/useApplications";

interface ApplicationsListProps {
  applications?: ApplicationSummary[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

function formatDate(value: string | undefined, locale: string, fallback: string): string {
  if (!value) {
    return fallback;
  }
  try {
    return new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(new Date(value));
  } catch {
    return fallback;
  }
}

export function ApplicationsList({
  applications,
  isLoading = false,
  isError = false,
  onRetry,
}: ApplicationsListProps) {
  const t = useTranslations("Dashboard.home.applications");
  const locale = useLocale();

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("title")}</CardTitle>
        <CardDescription>{t("subtitle")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <p className="text-sm text-muted-foreground">{t("loading")}</p>
        ) : null}

        {isError ? (
          <div className="flex flex-col items-start gap-3">
            <p className="text-sm text-destructive">{t("error")}</p>
            {onRetry ? (
              <Button variant="outline" size="sm" onClick={onRetry}>
                {t("retry")}
              </Button>
            ) : null}
          </div>
        ) : null}

        {!isLoading && !isError && (!applications || applications.length === 0) ? (
          <p className="text-sm text-muted-foreground">{t("empty")}</p>
        ) : null}

        {!isLoading && !isError && applications && applications.length > 0 ? (
          <div className="space-y-3">
            {applications.map((application) => {
              const statusKey = application.status?.toLowerCase() ?? "unknown";
              return (
                <div
                  key={application.id}
                  className="rounded-lg border bg-background p-4 shadow-sm"
                >
                  <div className="flex flex-col gap-1">
                    <p className="text-base font-semibold">{application.title}</p>
                    <p className="text-sm text-muted-foreground">{application.company}</p>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    <span className="rounded-full bg-muted px-2 py-1 font-medium text-foreground">
                      {t(`status.${statusKey}`)}
                    </span>
                    <span>{formatDate(application.updated_at ?? application.created_at, locale, t("unknownDate"))}</span>
                    {application.source ? <span>{t("source", { value: application.source })}</span> : null}
                  </div>
                </div>
              );
            })}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
