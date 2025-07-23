/**
 * Theme Provider - Central theme management for the application
 * Provides theme context and manages light/dark mode switching
 */

import type React from "react";
import { createContext, useContext, useEffect, useState } from "react";
import logger from "@/logger";
import { type ThemeMode, themeColors } from "./colors";

// Theme context type
interface ThemeContextType {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  toggleMode: () => void;
  colors: typeof themeColors.light | typeof themeColors.dark;
}

// Create theme context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Local storage key for theme persistence
const THEME_STORAGE_KEY = "reviewpoint-theme";

// Default theme mode
const DEFAULT_THEME: ThemeMode = "light";

/**
 * Theme Provider Component
 */
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: ThemeMode;
  enableSystem?: boolean;
}

export function ThemeProvider({
  children,
  defaultTheme = DEFAULT_THEME,
  enableSystem = true,
  ...props
}: ThemeProviderProps) {
  const [mode, setModeState] = useState<ThemeMode>(defaultTheme);

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    try {
      // Check localStorage first
      const storedTheme = localStorage.getItem(
        THEME_STORAGE_KEY,
      ) as ThemeMode | null;

      if (storedTheme && (storedTheme === "light" || storedTheme === "dark")) {
        setModeState(storedTheme);
        logger.info("Theme loaded from localStorage", { theme: storedTheme });
        return;
      }

      // Fallback to system preference if enabled
      if (enableSystem && window.matchMedia) {
        const systemPrefersDark = window.matchMedia(
          "(prefers-color-scheme: dark)",
        ).matches;
        const systemTheme: ThemeMode = systemPrefersDark ? "dark" : "light";
        setModeState(systemTheme);
        logger.info("Theme detected from system preference", {
          theme: systemTheme,
        });
        return;
      }

      // Final fallback to default
      setModeState(defaultTheme);
      logger.info("Using default theme", { theme: defaultTheme });
    } catch (error) {
      logger.error("Error initializing theme", error);
      setModeState(defaultTheme);
    }
  }, [defaultTheme, enableSystem]);

  // Apply theme to document root
  useEffect(() => {
    try {
      const root = window.document.documentElement;

      // Remove existing theme classes
      root.classList.remove("light", "dark");

      // Add current theme class
      root.classList.add(mode);

      // Apply CSS custom properties
      const colors = themeColors[mode];
      Object.entries(colors).forEach(([key, value]) => {
        // Convert camelCase to kebab-case for CSS variables
        const cssKey = key.replace(/([A-Z])/g, "-$1").toLowerCase();
        root.style.setProperty(`--color-${cssKey}`, value);
      });

      logger.debug("Theme applied to document", {
        mode,
        colorsCount: Object.keys(colors).length,
      });
    } catch (error) {
      logger.error("Error applying theme to document", error);
    }
  }, [mode]);

  // Set theme mode with persistence
  const setMode = (newMode: ThemeMode) => {
    try {
      setModeState(newMode);
      localStorage.setItem(THEME_STORAGE_KEY, newMode);
      logger.info("Theme mode changed", { from: mode, to: newMode });
    } catch (error) {
      logger.error("Error saving theme to localStorage", error);
      setModeState(newMode); // Still apply the theme even if storage fails
    }
  };

  // Toggle between light and dark modes
  const toggleMode = () => {
    const newMode: ThemeMode = mode === "light" ? "dark" : "light";
    setMode(newMode);
    logger.info("Theme toggled", { from: mode, to: newMode });
  };

  // Get current theme colors
  const colors = themeColors[mode];

  const value: ThemeContextType = {
    mode,
    setMode,
    toggleMode,
    colors,
  };

  return (
    <ThemeContext.Provider {...props} value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to use theme context
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    const error = "useTheme must be used within a ThemeProvider";
    logger.error(error);
    throw new Error(error);
  }

  return context;
}

/**
 * Hook to get current theme mode only (lighter alternative)
 */
export function useThemeMode(): ThemeMode {
  const { mode } = useTheme();
  return mode;
}

/**
 * Hook to get current theme colors only
 */
export function useThemeColors() {
  const { colors } = useTheme();
  return colors;
}

/**
 * System theme detection hook
 */
export function useSystemTheme(): ThemeMode {
  const [systemTheme, setSystemTheme] = useState<ThemeMode>("light");

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return;
    }

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    // eslint-disable-next-line no-undef
    const handleChange = (e: MediaQueryListEvent) => {
      const newTheme: ThemeMode = e.matches ? "dark" : "light";
      setSystemTheme(newTheme);
      logger.debug("System theme changed", { theme: newTheme });
    };

    // Initial check
    setSystemTheme(mediaQuery.matches ? "dark" : "light");

    // Listen for changes
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return systemTheme;
}
