"use client";

import { useEffect } from "react";
import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/store";

export type UserProfile = {
  id: string;
  email: string;
  full_name?: string;
  time_zone?: string | null;
  locale?: string | null;
};

export function useProtectedUserProfile() {
  const locale = useLocale();
  const router = useRouter();
  const { setUser, logout } = useAuth();

  const query = useQuery<UserProfile, Error>({
    queryKey: ["me"],
    queryFn: () => apiGet<UserProfile>("/users/me"),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  useEffect(() => {
    if (query.data) {
      setUser(query.data);
    }
  }, [query.data, setUser]);

  useEffect(() => {
    if (!query.error) {
      return;
    }

    if (query.error.message.includes("401")) {
      logout();
      router.replace(`/${locale}/login`);
    }
  }, [locale, logout, query.error, router]);

  return query;
}
