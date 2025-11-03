"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGetAuthorized } from "@/lib/api";
import { useAuth } from "@/lib/store";

export type ApplicationSummary = {
  id: number;
  title: string;
  company: string;
  status: string;
  source?: string | null;
  created_at?: string;
  updated_at?: string;
};

export function useApplications() {
  const { token, logout } = useAuth();

  const query = useQuery<ApplicationSummary[], Error>({
    queryKey: ["applications"],
    enabled: Boolean(token),
    staleTime: 60 * 1000,
    queryFn: () => {
      if (!token) {
        throw new Error("API Error 401");
      }

      return apiGetAuthorized<ApplicationSummary[]>("/applications", token);
    },
  });

  useEffect(() => {
    if (query.error && query.error.message.includes("401")) {
      logout();
    }
  }, [logout, query.error]);

  return query;
}
