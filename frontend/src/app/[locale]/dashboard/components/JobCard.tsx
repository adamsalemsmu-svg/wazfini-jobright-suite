"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import type { JobSummary } from "@/hooks/useJobsFeed";

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

  const postedRelative = formatRelativeDay(job.posted_date ?? undefined, locale, t("unknownDate"));
  const salary = formatSalary(job.salary_low, job.salary_high, job.currency, locale);

  return (
    <article className="flex h-full flex-col justify-between rounded-lg border bg-background p-4 shadow-sm">
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-foreground">{job.title}</h3>
        <p className="text-sm text-muted-foreground">{job.company}</p>
      </div>

      <div className="mt-4 space-y-2 text-sm text-muted-foreground">
        {job.location ? <p>{job.location}</p> : null}
        {salary.hasValue ? <p>{t("salary", { value: salary.label })}</p> : null}
        {job.job_type ? <p>{job.job_type}</p> : null}
        <p>{t("posted", { value: postedRelative })}</p>
        {job.source ? <p>{t("source", { value: job.source })}</p> : null}
      </div>

      {job.apply_url ? (
        <Link
          href={job.apply_url}
          target="_blank"
          rel="noreferrer"
          className="mt-4 text-sm font-medium text-primary underline-offset-4 hover:underline"
        >
          {t("cta")}
        </Link>
      ) : null}
    </article>
  );
}
