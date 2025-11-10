"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { useMutation } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import type { JobSummary } from "@/hooks/useJobsFeed";
import { apiPostAuthorized } from "@/lib/api";
import { useNotifications } from "@/lib/notifications";
import { useAuth } from "@/lib/store";
import { cn } from "@/lib/utils";

type AutomationResponse = {
  task_id: string;
  status: string;
};

interface JobCardProps {
  job: JobSummary;
}

function formatRelativeDay(value: string | null | undefined, locale: string, fallback: string): string {
  if (!value) {
    return fallback;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return fallback;
  }

  const now = new Date();
  const diffMs = parsed.getTime() - now.getTime();
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });
  return formatter.format(diffDays, "day");
}

function formatSalary(
  low: number | null | undefined,
  high: number | null | undefined,
  currency: string | null | undefined,
  locale: string
): { label: string; hasValue: boolean } {
  if (low == null && high == null) {
    return { label: "", hasValue: false };
  }

  const resolvedCurrency = currency && currency.length === 3 ? currency : undefined;
  const formatter = new Intl.NumberFormat(locale, {
    style: resolvedCurrency ? "currency" : "decimal",
    currency: resolvedCurrency ?? "USD",
    maximumFractionDigits: 0,
  });

  if (low != null && high != null) {
    return {
      label: `${formatter.format(low)} – ${formatter.format(high)}`,
      hasValue: true,
    };
  }

  const value = low ?? high ?? 0;
  return {
    label: formatter.format(value),
    hasValue: true,
  };
}

export function JobCard({ job }: JobCardProps) {
  const t = useTranslations("Dashboard.home.jobs");
  const locale = useLocale();
  const { token, user } = useAuth();
  const { push } = useNotifications();

  const postedRelative = formatRelativeDay(job.posted_date ?? undefined, locale, t("unknownDate"));
  const salary = formatSalary(job.salary_low, job.salary_high, job.currency, locale);
  const state = job.state ?? "recommended";

  const stateLabel = {
    recommended: t("states.recommended"),
    saved: t("states.saved"),
    applied: t("states.applied"),
  }[state];

  const stateClassName = {
    recommended: "bg-muted/40 text-muted-foreground",
    saved: "bg-amber-100 text-amber-800",
    applied: "bg-emerald-100 text-emerald-800",
  }[state];

  const normalizedSource = job.source?.toLowerCase() ?? "";
  const automationPlatform = normalizedSource.includes("greenhouse")
    ? "greenhouse"
    : normalizedSource.includes("workday")
    ? "workday"
    : normalizedSource.includes("bayt")
    ? "bayt"
    : null;

  const automationMutation = useMutation<AutomationResponse, Error>({
    mutationFn: async () => {
      if (!token) {
        throw new Error("Unauthorized");
      }
      if (!job.apply_url) {
        throw new Error("Missing apply URL");
      }
      if (!automationPlatform) {
        throw new Error("Unsupported platform");
      }

      const [firstName = "", ...rest] = (user?.full_name ?? "").split(" ");
      const body = {
        platform: automationPlatform,
        job_url: job.apply_url,
        profile: {
          first_name: firstName,
          last_name: rest.join(" ") || undefined,
          email: user?.email,
        },
        notify_email: user?.email,
      };

      return apiPostAuthorized<AutomationResponse>("/jobs/run", body, token);
    },
    onSuccess: (data: AutomationResponse) => {
      push({
        title: t("automationQueued"),
        message: t("automationQueuedMessage", { id: data.task_id }),
        read: false,
      });
    },
    onError: (error: Error) => {
      push({
        title: t("automationFailed"),
        message: error.message,
        read: false,
      });
    },
  });

  return (
    <article className="flex h-full flex-col justify-between rounded-lg border bg-background p-4 shadow-sm">
      <div className="space-y-1">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-base font-semibold text-foreground">{job.title}</h3>
            <p className="text-sm text-muted-foreground">{job.company}</p>
          </div>
          <span
            className={cn(
              "rounded-full px-2 py-0.5 text-xs font-medium capitalize",
              stateClassName
            )}
          >
            {stateLabel}
          </span>
        </div>
      </div>

      <div className="mt-4 space-y-2 text-sm text-muted-foreground">
        {job.location ? <p>{job.location}</p> : null}
        {salary.hasValue ? <p>{t("salary", { value: salary.label })}</p> : null}
        {job.job_type ? <p>{job.job_type}</p> : null}
        <p>{t("posted", { value: postedRelative })}</p>
        {job.source ? <p>{t("source", { value: job.source })}</p> : null}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {job.apply_url ? (
          <Link
            href={job.apply_url}
            target="_blank"
            rel="noreferrer"
            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            {t("cta")}
          </Link>
        ) : null}
        {automationPlatform && job.apply_url ? (
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={() => automationMutation.mutate()}
            disabled={automationMutation.isPending || !token}
          >
            {automationMutation.isPending ? t("automationPending") : t("automationCta")}
          </Button>
        ) : (
          <span className="text-xs text-muted-foreground">{t("automationUnavailable")}</span>
        )}
      </div>
    </article>
  );
}
