/**
 * UI Store - Enhanced for Phase 2.4 Design System
 * Manages UI state including theme, notifications, modals, and loading states
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ThemeMode } from "@/lib/theme/colors";
import logger from "@/logger";

// Notification types
export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message?: string;
  duration?: number; // ms, undefined means no auto-dismiss
  persistent?: boolean;
}

// Modal state
export interface ModalState {
  isOpen: boolean;
  type?: "confirm" | "alert" | "custom";
  title?: string;
  content?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

// Loading state
export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number; // 0-100
}

// UI Store Interface
interface UIState {
  // Theme state (synced with ThemeProvider)
  theme: ThemeMode;
  systemTheme: ThemeMode;
  followSystemTheme: boolean;

  // Layout state
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;

  // Notification system
  notifications: Notification[];

  // Modal system
  modal: ModalState;

  // Loading system
  loading: LoadingState;

  // Responsive state
  isMobile: boolean;

  // Actions
  setTheme: (theme: ThemeMode) => void;
  setSystemTheme: (theme: ThemeMode) => void;
  setFollowSystemTheme: (follow: boolean) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebarCollapsed: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;

  // Notification actions
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;

  // Modal actions
  openModal: (modal: Omit<ModalState, "isOpen">) => void;
  closeModal: () => void;

  // Loading actions
  setLoading: (loading: boolean, message?: string, progress?: number) => void;
  updateLoadingProgress: (progress: number) => void;

  // Responsive actions
  setIsMobile: (isMobile: boolean) => void;
}

// Generate unique ID for notifications
const generateId = (): string => {
  return `notification-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
};

// Default states
const defaultModalState: ModalState = {
  isOpen: false,
};

const defaultLoadingState: LoadingState = {
  isLoading: false,
};

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      // Initial state
      theme: "light",
      systemTheme: "light",
      followSystemTheme: true,
      sidebarOpen: false,
      sidebarCollapsed: false,
      notifications: [],
      modal: defaultModalState,
      loading: defaultLoadingState,
      isMobile: false,

      // Theme actions
      setTheme: (theme: ThemeMode) => {
        if (theme !== "light" && theme !== "dark") {
          const error = new Error(
            `Invalid theme provided: ${theme}. Expected 'light' or 'dark'.`,
          );
          logger.error("Invalid theme provided", { theme, error });
          throw error;
        }
        set({ theme });
        logger.info("Theme changed", { theme });
      },

      setSystemTheme: (systemTheme: ThemeMode) => {
        set({ systemTheme });

        // If following system theme, update current theme
        const { followSystemTheme } = get();
        if (followSystemTheme) {
          set({ theme: systemTheme });
          logger.info("Theme updated to follow system", { systemTheme });
        }
      },

      setFollowSystemTheme: (follow: boolean) => {
        set({ followSystemTheme: follow });

        // If enabling system follow, update to system theme
        if (follow) {
          const { systemTheme } = get();
          set({ theme: systemTheme });
          logger.info("Enabled follow system theme", { systemTheme });
        }
      },

      // Sidebar actions
      toggleSidebar: () => {
        set((state) => {
          const newOpen = !state.sidebarOpen;
          logger.debug("Sidebar toggled", {
            from: state.sidebarOpen,
            to: newOpen,
          });
          return { sidebarOpen: newOpen };
        });
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
        logger.debug("Sidebar state set", { open });
      },

      toggleSidebarCollapsed: () => {
        set((state) => {
          const newCollapsed = !state.sidebarCollapsed;
          logger.debug("Sidebar collapsed toggled", {
            from: state.sidebarCollapsed,
            to: newCollapsed,
          });
          return { sidebarCollapsed: newCollapsed };
        });
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
        logger.debug("Sidebar collapsed state set", { collapsed });
      },

      // Notification actions
      addNotification: (notification: Omit<Notification, "id">) => {
        if (!notification.title?.trim()) {
          const error = new Error("Notification title required");
          logger.error("Notification title is required", {
            notification,
            error,
          });
          throw error;
        }

        const newNotification: Notification = {
          ...notification,
          id: generateId(),
        };

        set((state) => ({
          notifications: [...state.notifications, newNotification],
        }));

        logger.info("Notification added", {
          type: newNotification.type,
          title: newNotification.title,
          id: newNotification.id,
        });

        // Auto-dismiss if duration is specified
        if (newNotification.duration && !newNotification.persistent) {
          setTimeout(() => {
            get().removeNotification(newNotification.id);
          }, newNotification.duration);
        }
      },

      removeNotification: (id: string) => {
        if (!id?.trim()) {
          const error = new Error(
            "Invalid notification ID: ID cannot be empty.",
          );
          logger.error("Invalid notification ID provided", { id, error });
          throw error;
        }

        const state = get();
        const notificationExists = state.notifications.some((n) => n.id === id);

        if (!notificationExists) {
          const error = new Error(`Notification not found with ID: ${id}`);
          logger.error("Notification not found", {
            id,
            error,
            existingIds: state.notifications.map((n) => n.id),
          });
          throw error;
        }

        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
        logger.debug("Notification removed", { id });
      },

      clearNotifications: () => {
        set({ notifications: [] });
        logger.info("All notifications cleared");
      },

      // Modal actions
      openModal: (modal: Omit<ModalState, "isOpen">) => {
        set({ modal: { ...modal, isOpen: true } });
        logger.debug("Modal opened", { type: modal.type, title: modal.title });
      },

      closeModal: () => {
        set({ modal: defaultModalState });
        logger.debug("Modal closed");
      },

      // Loading actions
      setLoading: (isLoading: boolean, message?: string, progress?: number) => {
        set({
          loading: {
            isLoading,
            message,
            progress,
          },
        });
        logger.debug("Loading state changed", { isLoading, message, progress });
      },

      updateLoadingProgress: (progress: number) => {
        const clampedProgress = Math.max(0, Math.min(100, progress));
        set((state) => ({
          loading: {
            ...state.loading,
            progress: clampedProgress,
          },
        }));
        logger.debug("Loading progress updated", { progress: clampedProgress });
      },

      // Responsive actions
      setIsMobile: (isMobile: boolean) => {
        set({ isMobile });
        logger.debug("Mobile state changed", { isMobile });
      },
    }),
    {
      name: "reviewpoint-ui-store",
      partialize: (state) => ({
        theme: state.theme,
        followSystemTheme: state.followSystemTheme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    },
  ),
);
