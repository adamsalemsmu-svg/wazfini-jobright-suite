import { create } from "zustand";

type AuthUser = {
  id?: string;
  email?: string;
  full_name?: string;
  [key: string]: unknown;
};

type LoginPayload = {
  user: AuthUser;
  access_token?: string;
  refresh_token?: string;
};

type AuthState = {
  user: AuthUser | null;
  token: string | null;
  login: (payload: LoginPayload) => void;
  logout: () => void;
};

export const useAuth = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: ({ user, access_token }) =>
    set({
      user,
      token: access_token ?? null,
    }),
  logout: () => set({ user: null, token: null }),
}));
