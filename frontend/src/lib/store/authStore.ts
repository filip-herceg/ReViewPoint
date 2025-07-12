import { create } from "zustand";
import logger from "@/logger";

interface AuthUser {
  id: string;
  email: string;
  name: string;
  roles: string[];
  bio?: string;
  avatar_url?: string;
  created_at?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthState {
  user: AuthUser | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isRefreshing: boolean;
  isLoading: boolean;
  error: string | null;
  login: (user: AuthUser, tokens: AuthTokens) => void;
  logout: () => void;
  setTokens: (tokens: AuthTokens) => void;
  setRefreshing: (isRefreshing: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  clearTokens: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isRefreshing: false,
  isLoading: false,
  error: null,

  login: (user, tokens) => {
    if (!user || !tokens) {
      const error = new Error("User and tokens required for login");
      logger.error("[AuthStore] Login failed", { error: error.message });
      throw error;
    }

    logger.info("[AuthStore] User login successful", {
      userId: user.id,
      email: user.email,
    });
    set({
      user,
      tokens,
      isAuthenticated: true,
      isRefreshing: false,
      isLoading: false,
      error: null,
    });
  },

  logout: () => {
    logger.info("[AuthStore] User logout");
    set({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isRefreshing: false,
      isLoading: false,
      error: null,
    });
  },

  setTokens: (tokens) => {
    if (!tokens?.access_token) {
      const error = new Error("Invalid tokens provided");
      logger.error("[AuthStore] Set tokens failed", { error: error.message });
      throw error;
    }

    logger.debug("[AuthStore] Tokens updated", {
      hasAccessToken: !!tokens.access_token,
      hasRefreshToken: !!tokens.refresh_token,
    });
    set({ tokens, isAuthenticated: !!tokens.access_token });
  },

  setRefreshing: (isRefreshing) => {
    logger.debug("[AuthStore] Set refreshing state", { isRefreshing });
    set({ isRefreshing });
  },

  setLoading: (isLoading) => {
    logger.debug("[AuthStore] Set loading state", { isLoading });
    set({ isLoading });
  },

  setError: (error) => {
    logger.debug("[AuthStore] Set error state", { error });
    set({ error });
  },

  clearError: () => {
    logger.debug("[AuthStore] Clearing error");
    set({ error: null });
  },

  clearTokens: () => {
    logger.debug("[AuthStore] Clearing tokens");
    set({ tokens: null, isAuthenticated: false });
  },
}));

// Utility to get the current token outside React components
export function getToken() {
  const tokens = useAuthStore.getState().tokens;
  return tokens?.access_token;
}

// Utility to get the current refresh token
export function getRefreshToken() {
  const tokens = useAuthStore.getState().tokens;
  return tokens?.refresh_token;
}
