"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/lib/store";
import { useProtectedUserProfile } from "@/hooks/useProtectedUserProfile";

export default function DashboardPage() {
  const t = useTranslations("Dashboard.profile");
  const { user: authUser } = useAuth();
  const { data: profile, isLoading, error, refetch, isRefetching } = useProtectedUserProfile();

  const displayName = useMemo(() => {
    return (
      profile?.full_name ??
      profile?.email ??
      authUser?.full_name ??
      authUser?.email ??
      ""
    );
  }, [authUser?.email, authUser?.full_name, profile?.email, profile?.full_name]);

  if (isLoading || isRefetching) {
    return (
      <div className="flex h-full flex-col justify-center gap-2">
        <p className="text-sm text-muted-foreground">{t("loading")}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-start justify-center gap-4">
        <p className="text-sm text-destructive">{t("error")}</p>
        <button
          type="button"
          className="text-sm font-medium text-primary underline-offset-4 hover:underline"
          onClick={() => refetch()}
        >
          {t("retry")}
        </button>
      </div>
    );
  }

  const timeZone = profile?.time_zone || t("timezoneUnset");

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t("heading", { name: displayName })}
        </h1>
        <p className="text-sm text-muted-foreground">{t("subheading")}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("details.title")}</CardTitle>
            <CardDescription>{t("details.subtitle")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <p className="font-medium text-muted-foreground">{t("details.email")}</p>
              <p className="font-semibold">{profile?.email}</p>
            </div>
            <div>
              <p className="font-medium text-muted-foreground">{t("details.timezone")}</p>
              <p className="font-semibold">{timeZone}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("activity.title")}</CardTitle>
            <CardDescription>{t("activity.subtitle")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>{t("activity.tip1")}</p>
            <p>{t("activity.tip2")}</p>
            <p>{t("activity.tip3")}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
