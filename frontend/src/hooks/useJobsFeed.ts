"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiPostAuthorized } from "@/lib/api";
import { useAuth } from "@/lib/store";

export type JobSummary = {
  id: number | string;
  title: string;
  company: string;
  location?: string | null;
  salary_low?: number | null;
  salary_high?: number | null;
  currency?: string | null;
  job_type?: string | null;
  experience_level?: string | null;
  industry?: string | null;
  education_level?: string | null;
  work_mode?: string | null;
  posted_date?: string | null;
  apply_url?: string | null;
  description?: string | null;
  source?: string | null;
  state?: "recommended" | "saved" | "applied";
};

export function useJobsFeed() {
  const { token, logout } = useAuth();

  const query = useQuery<JobSummary[], Error>({
    queryKey: ["jobs", "recommended"],
    enabled: Boolean(token),
    staleTime: 2 * 60 * 1000,
    queryFn: () => {
      if (!token) {
        throw new Error("API Error 401");
      }

      return apiPostAuthorized<JobSummary[]>("/jobs/search", {}, token);
    },
  });

  useEffect(() => {
    if (query.error && query.error.message.includes("401")) {
      logout();
    }
  }, [logout, query.error]);

  return query;
}
