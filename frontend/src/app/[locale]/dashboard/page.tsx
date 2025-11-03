"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import { ApplicationsList } from "./components/ApplicationsList";
import { DashboardHeader } from "./components/DashboardHeader";
import { JobCard } from "./components/JobCard";
import { UserCard } from "./components/UserCard";
import { AssistantPanel } from "./components/assistant/AssistantPanel";
import { useApplications } from "@/hooks/useApplications";
import { useJobsFeed } from "@/hooks/useJobsFeed";
import { useProtectedUserProfile } from "@/hooks/useProtectedUserProfile";
import { useAuth } from "@/lib/store";

export default function DashboardPage() {
  const overviewT = useTranslations("Dashboard.home");
  const jobsT = useTranslations("Dashboard.home.jobs");
  const { user: authUser } = useAuth();

  const profileQuery = useProtectedUserProfile();
  const applicationsQuery = useApplications();
  const jobsQuery = useJobsFeed();

  const isProfileLoading = profileQuery.isLoading || profileQuery.isFetching;
  const hasProfileError = Boolean(profileQuery.error);

  const displayName = useMemo(() => {
    const profile = profileQuery.data;
    return (
      profile?.full_name ??
      profile?.email ??
      authUser?.full_name ??
      authUser?.email ??
      ""
    );
  }, [authUser?.email, authUser?.full_name, profileQuery.data]);

  if (isProfileLoading) {
    return (
      <div className="flex min-h-[40vh] flex-col items-start justify-center gap-3">
        <p className="text-sm text-muted-foreground">{overviewT("loading")}</p>
      </div>
    );
  }

  if (hasProfileError || !profileQuery.data) {
    return (
      <div className="flex min-h-[40vh] flex-col items-start justify-center gap-4">
        <p className="text-sm text-destructive">{overviewT("error")}</p>
        <button
          type="button"
          className="text-sm font-medium text-primary underline-offset-4 hover:underline"
          onClick={() => profileQuery.refetch()}
        >
          {overviewT("retry")}
        </button>
      </div>
    );
  }

  const applications = applicationsQuery.data ?? [];
  const jobs = jobsQuery.data ?? [];
  const isRefreshing =
    profileQuery.isFetching || applicationsQuery.isFetching || jobsQuery.isFetching;

  const refreshAll = () => {
    void Promise.all([
      profileQuery.refetch(),
      applicationsQuery.refetch(),
      jobsQuery.refetch(),
    ]);
  };

  return (
    <div className="space-y-8">
      <DashboardHeader
        name={displayName}
        totalApplications={applications.length}
        totalJobs={jobs.length}
        refreshing={isRefreshing}
        onRefresh={refreshAll}
      />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <section className="space-y-6">
          <ApplicationsList
            applications={applications}
            isLoading={applicationsQuery.isLoading && !applicationsQuery.isError}
            isError={applicationsQuery.isError}
            onRetry={() => applicationsQuery.refetch()}
          />

          <section className="space-y-4">
            <div className="space-y-1">
              <h2 className="text-lg font-semibold text-foreground">
                {jobsT("title")}
              </h2>
              <p className="text-sm text-muted-foreground">{jobsT("subtitle")}</p>
            </div>

            {jobsQuery.isLoading && !jobsQuery.isError ? (
              <p className="text-sm text-muted-foreground">{jobsT("loading")}</p>
            ) : null}

            {jobsQuery.isError ? (
              <div className="flex flex-col items-start gap-3">
                <p className="text-sm text-destructive">{jobsT("error")}</p>
                <button
                  type="button"
                  className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                  onClick={() => jobsQuery.refetch()}
                >
                  {jobsT("retry")}
                </button>
              </div>
            ) : null}

            {!jobsQuery.isLoading && !jobsQuery.isError && jobs.length === 0 ? (
              <p className="text-sm text-muted-foreground">{jobsT("empty")}</p>
            ) : null}

            {!jobsQuery.isError && jobs.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {jobs.map((job) => (
                  <JobCard key={job.id} job={job} />
                ))}
              </div>
            ) : null}
          </section>
        </section>

        <aside className="space-y-6">
          <UserCard user={profileQuery.data} />
          <AssistantPanel profileId={profileQuery.data.id} />
        </aside>
      </div>
    </div>
  );
}
