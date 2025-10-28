"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useProtectedUserProfile } from "@/hooks/useProtectedUserProfile";
import { useAuth } from "@/lib/store";

export default function DashboardProfilePage() {
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
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">{t("loading")}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-3">
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
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">{t("heading", { name: displayName })}</h1>
        <p className="text-sm text-muted-foreground">{t("profileIntro")}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("details.title")}</CardTitle>
          <CardDescription>{t("details.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{t("details.email")}</p>
            <p className="text-base font-semibold">{profile?.email}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">{t("details.timezone")}</p>
            <p className="text-base font-semibold">{timeZone}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
