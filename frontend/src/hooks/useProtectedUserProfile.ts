"use client";

import { useEffect } from "react";
import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiGetAuthorized } from "@/lib/api";
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
  const { token, setUser, logout } = useAuth();

  const query = useQuery<UserProfile, Error>({
    queryKey: ["me"],
    queryFn: () => {
      if (!token) {
        throw new Error("API Error 401");
      }

      return apiGetAuthorized<UserProfile>("/users/me", token);
    },
    enabled: Boolean(token),
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
