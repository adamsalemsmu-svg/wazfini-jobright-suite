import { create } from 'zustand';

type AuthState = {
  user: any | null;
  token: string | null;
  login: (payload: { user: any; token: string }) => void;
  logout: () => void;
};

export const useAuth = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: (payload) => set({ user: payload.user, token: payload.token }),
  logout: () => set({ user: null, token: null })
}));
