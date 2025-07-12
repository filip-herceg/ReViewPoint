/**
 * Design System - Color Tokens
 * Central color palette for the ReViewPoint design system
 * Uses HSL values for better theme manipulation
 */

import logger from "@/logger";

// Primary brand colors
export const colors = {
  // Primary colors
  primary: {
    50: "hsl(210, 100%, 97%)",
    100: "hsl(210, 100%, 95%)",
    200: "hsl(210, 100%, 90%)",
    300: "hsl(210, 100%, 80%)",
    400: "hsl(210, 100%, 70%)",
    500: "hsl(210, 100%, 50%)", // Main primary
    600: "hsl(210, 100%, 45%)",
    700: "hsl(210, 100%, 40%)",
    800: "hsl(210, 100%, 35%)",
    900: "hsl(210, 100%, 25%)",
    950: "hsl(210, 100%, 15%)",
  },

  // Secondary/neutral colors
  secondary: {
    50: "hsl(210, 10%, 98%)",
    100: "hsl(210, 10%, 95%)",
    200: "hsl(210, 10%, 90%)",
    300: "hsl(210, 10%, 80%)",
    400: "hsl(210, 10%, 60%)",
    500: "hsl(210, 10%, 40%)",
    600: "hsl(210, 10%, 30%)",
    700: "hsl(210, 10%, 20%)",
    800: "hsl(210, 10%, 15%)",
    900: "hsl(210, 10%, 10%)",
    950: "hsl(210, 10%, 5%)",
  },

  // Accent colors
  accent: {
    50: "hsl(340, 75%, 97%)",
    100: "hsl(340, 75%, 95%)",
    200: "hsl(340, 75%, 90%)",
    300: "hsl(340, 75%, 80%)",
    400: "hsl(340, 75%, 70%)",
    500: "hsl(340, 75%, 50%)", // Main accent
    600: "hsl(340, 75%, 45%)",
    700: "hsl(340, 75%, 40%)",
    800: "hsl(340, 75%, 35%)",
    900: "hsl(340, 75%, 25%)",
    950: "hsl(340, 75%, 15%)",
  },

  // Semantic colors
  success: {
    50: "hsl(120, 50%, 97%)",
    100: "hsl(120, 50%, 95%)",
    200: "hsl(120, 50%, 90%)",
    300: "hsl(120, 50%, 80%)",
    400: "hsl(120, 50%, 70%)",
    500: "hsl(120, 50%, 50%)", // Main success
    600: "hsl(120, 50%, 45%)",
    700: "hsl(120, 50%, 40%)",
    800: "hsl(120, 50%, 35%)",
    900: "hsl(120, 50%, 25%)",
    950: "hsl(120, 50%, 15%)",
  },

  warning: {
    50: "hsl(45, 90%, 97%)",
    100: "hsl(45, 90%, 95%)",
    200: "hsl(45, 90%, 90%)",
    300: "hsl(45, 90%, 80%)",
    400: "hsl(45, 90%, 70%)",
    500: "hsl(45, 90%, 60%)", // Main warning
    600: "hsl(45, 90%, 55%)",
    700: "hsl(45, 90%, 50%)",
    800: "hsl(45, 90%, 45%)",
    900: "hsl(45, 90%, 35%)",
    950: "hsl(45, 90%, 25%)",
  },

  error: {
    50: "hsl(0, 75%, 97%)",
    100: "hsl(0, 75%, 95%)",
    200: "hsl(0, 75%, 90%)",
    300: "hsl(0, 75%, 80%)",
    400: "hsl(0, 75%, 70%)",
    500: "hsl(0, 75%, 60%)", // Main error
    600: "hsl(0, 75%, 55%)",
    700: "hsl(0, 75%, 50%)",
    800: "hsl(0, 75%, 45%)",
    900: "hsl(0, 75%, 35%)",
    950: "hsl(0, 75%, 25%)",
  },
} as const;

export type ColorScale = keyof typeof colors;
export type ColorShade = keyof typeof colors.primary;

/**
 * Get a color value by scale and shade
 */
export function getColor(scale: ColorScale, shade: ColorShade): string {
  const colorValue = colors[scale][shade];
  if (!colorValue) {
    logger.warn("Invalid color requested", { scale, shade });
    return colors.secondary[500]; // Fallback color
  }

  logger.debug("Retrieved color", { scale, shade, value: colorValue });
  return colorValue;
}

/**
 * Theme color mappings for light and dark modes
 */
export const themeColors = {
  light: {
    background: colors.secondary[50],
    foreground: colors.secondary[900],
    card: colors.secondary[100],
    cardForeground: colors.secondary[800],
    popover: colors.secondary[100],
    popoverForeground: colors.secondary[800],
    primary: colors.primary[500],
    primaryForeground: colors.secondary[50],
    secondary: colors.secondary[200],
    secondaryForeground: colors.secondary[700],
    muted: colors.secondary[200],
    mutedForeground: colors.secondary[600],
    accent: colors.accent[200],
    accentForeground: colors.accent[800],
    destructive: colors.error[500],
    destructiveForeground: colors.secondary[50],
    border: colors.secondary[300],
    input: colors.secondary[300],
    ring: colors.primary[500],
  },
  dark: {
    background: colors.secondary[950],
    foreground: colors.secondary[100],
    card: colors.secondary[900],
    cardForeground: colors.secondary[200],
    popover: colors.secondary[900],
    popoverForeground: colors.secondary[200],
    primary: colors.primary[400],
    primaryForeground: colors.secondary[950],
    secondary: colors.secondary[800],
    secondaryForeground: colors.secondary[300],
    muted: colors.secondary[800],
    mutedForeground: colors.secondary[400],
    accent: colors.accent[700],
    accentForeground: colors.accent[200],
    destructive: colors.error[400],
    destructiveForeground: colors.secondary[100],
    border: colors.secondary[700],
    input: colors.secondary[700],
    ring: colors.primary[400],
  },
} as const;

export type ThemeMode = keyof typeof themeColors;
export type ThemeColorKey = keyof typeof themeColors.light;

/**
 * Get theme color value
 */
export function getThemeColor(
  mode: ThemeMode,
  colorKey: ThemeColorKey,
): string {
  const colorValue = themeColors[mode][colorKey];
  if (!colorValue) {
    logger.warn("Invalid theme color requested", { mode, colorKey });
    return themeColors.light.background; // Fallback
  }

  logger.debug("Retrieved theme color", { mode, colorKey, value: colorValue });
  return colorValue;
}
