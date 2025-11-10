"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApplications } from "@/hooks/useApplications";
import { useJobsFeed, type JobSummary } from "@/hooks/useJobsFeed";
import { useProtectedUserProfile } from "@/hooks/useProtectedUserProfile";

import { DashboardHeader } from "./components/DashboardHeader";
import { ApplicationsList } from "./components/ApplicationsList";
import { JobCard } from "./components/JobCard";
import { UserCard } from "./components/UserCard";
import { AssistantPanel } from "./components/assistant/AssistantPanel";
import AnalyticsSummary from "./components/AnalyticsSummary";

export default function DashboardPage() {
  const router = useRouter();
  const {
    data: user,
    isLoading: userLoading,
    error: userError,
  } = useProtectedUserProfile();
  const {
    data: applications,
    isLoading: appsLoading,
    error: appsError,
    refetch: refetchApps,
  } = useApplications();
  const {
    data: jobs,
    isLoading: jobsLoading,
    error: jobsError,
    refetch: refetchJobs,
  } = useJobsFeed();

  // Redirect unauthenticated users
  useEffect(() => {
    if (!userLoading && !user) router.push("/en/login");
  }, [user, userLoading, router]);

  if (userError) return <div className="p-6 text-red-500">Error loading profile: {userError.message}</div>;
  if (userLoading) return <div className="p-6 text-gray-500">Loading your dashboard...</div>;

  return (
    <main className="flex flex-col gap-6 p-6 md:p-8 bg-gray-50 min-h-screen">
      {/* ✅ Dashboard Header */}
      <DashboardHeader
        name={user?.full_name ?? user?.email ?? ""}
        totalApplications={applications?.length ?? 0}
        totalJobs={jobs?.length ?? 0}
        onRefresh={() => {
          void refetchApps();
          void refetchJobs();
        }}
        refreshing={appsLoading || jobsLoading}
      />

      {/* ✅ Analytics Summary */}
      <AnalyticsSummary />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* ✅ User Profile Card */}
        <section className="md:col-span-1">
          <UserCard user={user} />
        </section>

        {/* ✅ Job Applications */}
        <section className="md:col-span-2 space-y-6">
          <ApplicationsList
            applications={applications || []}
            isLoading={appsLoading}
            isError={Boolean(appsError)}
            onRetry={appsError ? () => void refetchApps() : undefined}
          />

          {/* ✅ Recommended Jobs */}
          <div>
            <h2 className="text-lg font-semibold mb-2 text-gray-800">Recommended Jobs</h2>
            {jobsLoading ? (
              <p className="text-gray-500">Loading jobs...</p>
            ) : jobsError ? (
              <p className="text-red-500">Error loading jobs</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {jobs?.length ? (
                  jobs.map((job: JobSummary) => <JobCard key={job.id} job={job} />)
                ) : (
                  <p className="text-gray-500">No jobs found.</p>
                )}
              </div>
            )}
          </div>
        </section>
      </div>

      {/* ✅ Assistant Panel */}
      <AssistantPanel />
    </main>
  );
}
