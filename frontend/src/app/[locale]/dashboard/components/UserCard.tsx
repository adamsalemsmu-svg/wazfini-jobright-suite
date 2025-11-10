"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { UserProfile } from "@/hooks/useProtectedUserProfile";

interface UserCardProps {
  user?: UserProfile | null;
}

export function UserCard({ user }: UserCardProps) {
  const t = useTranslations("Dashboard.home.userCard");
  const locale = useLocale();

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("title")}</CardTitle>
        <CardDescription>{t("subtitle")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div>
          <p className="font-medium text-muted-foreground">{t("fields.name")}</p>
          <p className="font-semibold">{user?.full_name ?? t("fallbacks.name")}</p>
        </div>
        <div>
          <p className="font-medium text-muted-foreground">{t("fields.email")}</p>
          <p className="font-semibold break-all">{user?.email ?? t("fallbacks.email")}</p>
        </div>
        <div>
          <p className="font-medium text-muted-foreground">{t("fields.locale")}</p>
          <p className="font-semibold">{user?.locale ?? locale}</p>
        </div>
        <div>
          <p className="font-medium text-muted-foreground">{t("fields.timezone")}</p>
          <p className="font-semibold">{user?.time_zone ?? t("fallbacks.timezone")}</p>
        </div>
        {user?.phone ? (
          <div>
            <p className="font-medium text-muted-foreground">{t("fields.phone")}</p>
            <p className="font-semibold">{user.phone}</p>
          </div>
        ) : null}
        {user?.linkedin_url ? (
          <div>
            <p className="font-medium text-muted-foreground">{t("fields.linkedin")}</p>
            <Link
              href={user.linkedin_url}
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-primary underline-offset-4 hover:underline"
            >
              {user.linkedin_url}
            </Link>
          </div>
        ) : null}
        {user?.github_url ? (
          <div>
            <p className="font-medium text-muted-foreground">{t("fields.github")}</p>
            <Link
              href={user.github_url}
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-primary underline-offset-4 hover:underline"
            >
              {user.github_url}
            </Link>
          </div>
        ) : null}
        {user?.resume_skills?.length ? (
          <div>
            <p className="font-medium text-muted-foreground">{t("fields.skills")}</p>
            <p className="font-semibold">{user.resume_skills.join(", ")}</p>
          </div>
        ) : null}
        <div>
          <Link
            href={`/${locale}/dashboard/profile`}
            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            {t("cta")}
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
