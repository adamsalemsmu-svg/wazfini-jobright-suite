"use client";

import { FormEvent, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useProtectedUserProfile, type UserProfile } from "@/hooks/useProtectedUserProfile";
import { apiPostFormAuthorized } from "@/lib/api";
import { useAuth } from "@/lib/store";

type ResumeParsed = {
  email?: string | null;
  phone?: string | null;
  linkedin?: string | null;
  github?: string | null;
  skills?: string[] | null;
};

type ResumeUploadResponse = {
  parsed: ResumeParsed;
  user: UserProfile;
};

export default function DashboardProfilePage() {
  const t = useTranslations("Dashboard.profile");
  const { user: authUser, token } = useAuth();
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [parsed, setParsed] = useState<ResumeParsed | null>(null);
  const { data: profile, isLoading, error, refetch, isRefetching } = useProtectedUserProfile();

  const uploadMutation = useMutation<ResumeUploadResponse, Error, File>({
    mutationFn: async (file: File) => {
      if (!token) {
        throw new Error("Unauthorized");
      }
      const form = new FormData();
      form.append("file", file);
      return apiPostFormAuthorized<ResumeUploadResponse>("/upload/resume", form, token);
    },
    onSuccess: (data) => {
      setParsed(data.parsed);
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

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

  const handleUpload = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile || uploadMutation.isPending) {
      return;
    }
    uploadMutation.mutate(selectedFile);
  };

  const resumeSkills = profile?.resume_skills ?? [];

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
          {profile?.phone ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("details.phone")}</p>
              <p className="text-base font-semibold">{profile.phone}</p>
            </div>
          ) : null}
          {profile?.linkedin_url ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("details.linkedin")}</p>
              <a
                href={profile.linkedin_url}
                target="_blank"
                rel="noreferrer"
                className="text-base font-semibold text-primary underline-offset-4 hover:underline"
              >
                {profile.linkedin_url}
              </a>
            </div>
          ) : null}
          {profile?.github_url ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("details.github")}</p>
              <a
                href={profile.github_url}
                target="_blank"
                rel="noreferrer"
                className="text-base font-semibold text-primary underline-offset-4 hover:underline"
              >
                {profile.github_url}
              </a>
            </div>
          ) : null}
          {resumeSkills?.length ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("details.skills")}</p>
              <p className="text-base font-semibold">{resumeSkills.join(", ")}</p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("resume.title")}</CardTitle>
          <CardDescription>{t("resume.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form className="flex flex-col gap-3 sm:flex-row sm:items-center" onSubmit={handleUpload}>
            <Input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
            <Button type="submit" disabled={!selectedFile || uploadMutation.isPending}>
              {uploadMutation.isPending ? t("resume.uploading") : t("resume.uploadCta")}
            </Button>
          </form>
          {uploadMutation.isError ? (
            <p className="text-sm text-destructive">{t("resume.error")}</p>
          ) : null}
          {parsed ? (
            <div className="space-y-1 text-sm">
              {parsed.email ? <p>{t("resume.detectedEmail", { value: parsed.email })}</p> : null}
              {parsed.phone ? <p>{t("resume.detectedPhone", { value: parsed.phone })}</p> : null}
              {parsed.linkedin ? <p>{t("resume.detectedLinkedin", { value: parsed.linkedin })}</p> : null}
              {parsed.github ? <p>{t("resume.detectedGithub", { value: parsed.github })}</p> : null}
              {parsed.skills?.length ? (
                <p>{t("resume.detectedSkills", { value: parsed.skills.join(", ") })}</p>
              ) : null}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
