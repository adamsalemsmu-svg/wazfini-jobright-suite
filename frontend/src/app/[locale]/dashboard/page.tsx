"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/store";

export default function DashboardPage() {
  const t = useTranslations("Dashboard");
  const { user } = useAuth();

  const { data: health, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet<{ status: string }>("/health"),
    staleTime: 60_000,
  });

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>{t("welcome", { name: user?.full_name ?? user?.email ?? "" })}</CardTitle>
          <CardDescription>{t("subtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>{t("tips.0")}</li>
            <li>{t("tips.1")}</li>
            <li>{t("tips.2")}</li>
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("status.title")}</CardTitle>
          <CardDescription>{t("status.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-sm">
            {isLoading && <p>{t("status.loading")}</p>}
            {isError && <p className="text-destructive">{t("status.error")}</p>}
            {!isLoading && !isError && (
              <p className="font-medium text-emerald-600">{health?.status ?? t("status.unknown")}</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
