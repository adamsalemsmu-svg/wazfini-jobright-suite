"use client";

import { FormEvent, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiPost } from "@/lib/api";

export default function ResetPage() {
  const t = useTranslations("Auth.Reset");
  const locale = useLocale();

  const [requestEmail, setRequestEmail] = useState("");
  const [requestMessage, setRequestMessage] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [requestLoading, setRequestLoading] = useState(false);

  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [resetMessage, setResetMessage] = useState<string | null>(null);
  const [resetError, setResetError] = useState<string | null>(null);
  const [resetLoading, setResetLoading] = useState(false);

  const submitRequest = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setRequestError(null);
    setRequestMessage(null);
    setRequestLoading(true);
    try {
      await apiPost("/auth/request-reset", { email: requestEmail });
      setRequestMessage(t("requestSuccess"));
    } catch (error) {
      setRequestError(t("requestError"));
    } finally {
      setRequestLoading(false);
    }
  };

  const submitReset = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setResetError(null);
    setResetMessage(null);
    setResetLoading(true);
    try {
      await apiPost("/auth/reset", { token, password: newPassword });
      setResetMessage(t("resetSuccess"));
    } catch (error) {
      setResetError(t("resetError"));
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-4 py-12 md:flex-row">
      <Card className="w-full md:w-1/2">
        <CardHeader>
          <CardTitle>{t("requestTitle")}</CardTitle>
          <CardDescription>{t("requestSubtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          {requestError && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{requestError}</AlertDescription>
            </Alert>
          )}
          {requestMessage && (
            <Alert className="mb-4">
              <AlertDescription>{requestMessage}</AlertDescription>
            </Alert>
          )}
          <form onSubmit={submitRequest} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="requestEmail">{t("emailLabel")}</Label>
              <Input
                id="requestEmail"
                type="email"
                value={requestEmail}
                onChange={(event) => setRequestEmail(event.target.value)}
                placeholder={t("emailPlaceholder")}
                required
              />
            </div>
            <Button type="submit" disabled={requestLoading} className="w-full">
              {requestLoading ? t("loading") : t("requestSubmit")}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="text-sm text-muted-foreground">
          <Link href={`/${locale}/login`} className="text-primary hover:underline">
            {t("backToLogin")}
          </Link>
        </CardFooter>
      </Card>

      <Card className="w-full md:w-1/2">
        <CardHeader>
          <CardTitle>{t("resetTitle")}</CardTitle>
          <CardDescription>{t("resetSubtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          {resetError && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{resetError}</AlertDescription>
            </Alert>
          )}
          {resetMessage && (
            <Alert className="mb-4">
              <AlertDescription>{resetMessage}</AlertDescription>
            </Alert>
          )}
          <form onSubmit={submitReset} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="token">{t("tokenLabel")}</Label>
              <Input
                id="token"
                value={token}
                onChange={(event) => setToken(event.target.value)}
                placeholder={t("tokenPlaceholder")}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="newPassword">{t("newPasswordLabel")}</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                placeholder={t("newPasswordPlaceholder")}
                required
              />
            </div>
            <Button type="submit" disabled={resetLoading} className="w-full">
              {resetLoading ? t("loading") : t("resetSubmit")}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="text-sm text-muted-foreground">
          <span>{t("tokenHelp")}</span>
        </CardFooter>
      </Card>
    </div>
  );
}
