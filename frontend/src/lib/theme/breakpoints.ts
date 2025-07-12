/**
 * Design System - Responsive Breakpoints
 * Centralized breakpoint definitions for responsive design
 */

import logger from "@/logger";

// Breakpoint definitions (mobile-first)
export const breakpoints = {
  xs: "320px", // Extra small devices (small phones)
  sm: "640px", // Small devices (phones)
  md: "768px", // Medium devices (tablets)
  lg: "1024px", // Large devices (desktops)
  xl: "1280px", // Extra large devices (large desktops)
  "2xl": "1536px", // 2X large devices (larger desktops)
} as const;

// Container max-widths for each breakpoint
export const containerMaxWidths = {
  xs: "100%",
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
} as const;

// Grid system
export const gridSystem = {
  columns: 12,
  gutter: {
    xs: "1rem", // 16px
    sm: "1.5rem", // 24px
    md: "2rem", // 32px
    lg: "2.5rem", // 40px
    xl: "3rem", // 48px
    "2xl": "3.5rem", // 56px
  },
} as const;

export type Breakpoint = keyof typeof breakpoints;
export type ContainerMaxWidth = keyof typeof containerMaxWidths;

/**
 * Get breakpoint value by key
 */
export function getBreakpoint(breakpoint: Breakpoint): string {
  const value = breakpoints[breakpoint];
  if (!value) {
    logger.warn("Invalid breakpoint requested", { breakpoint });
    return breakpoints.md; // Fallback
  }

  logger.debug("Retrieved breakpoint value", { breakpoint, value });
  return value;
}

/**
 * Get container max-width for breakpoint
 */
export function getContainerMaxWidth(breakpoint: ContainerMaxWidth): string {
  const value = containerMaxWidths[breakpoint];
  if (!value) {
    logger.warn("Invalid container max-width requested", { breakpoint });
    return containerMaxWidths.lg; // Fallback
  }

  logger.debug("Retrieved container max-width", { breakpoint, value });
  return value;
}

/**
 * Generate media query string for breakpoint
 */
export function mediaQuery(breakpoint: Breakpoint): string {
  const value = getBreakpoint(breakpoint);
  const query = `@media (min-width: ${value})`;

  logger.debug("Generated media query", { breakpoint, query });
  return query;
}

/**
 * Generate media query for max-width (mobile-first approach)
 */
export function mediaQueryMax(breakpoint: Breakpoint): string {
  const value = getBreakpoint(breakpoint);
  // Subtract 1px to avoid overlap
  const maxValue = `${parseInt(value) - 1}px`;
  const query = `@media (max-width: ${maxValue})`;

  logger.debug("Generated max-width media query", { breakpoint, query });
  return query;
}

/**
 * Check if current viewport matches breakpoint (client-side only)
 */
export function matchesBreakpoint(breakpoint: Breakpoint): boolean {
  if (typeof window === "undefined") {
    logger.warn("matchesBreakpoint called on server-side");
    return false;
  }

  const value = getBreakpoint(breakpoint);
  const matches = window.matchMedia(`(min-width: ${value})`).matches;

  logger.debug("Checked breakpoint match", { breakpoint, matches });
  return matches;
}

/**
 * Get current active breakpoint (client-side only)
 */
export function getCurrentBreakpoint(): Breakpoint {
  if (typeof window === "undefined") {
    logger.warn("getCurrentBreakpoint called on server-side");
    return "md"; // Fallback for SSR
  }

  const width = window.innerWidth;

  // Check breakpoints from largest to smallest
  const breakpointEntries = Object.entries(breakpoints).sort(
    ([, a], [, b]) => parseInt(b) - parseInt(a),
  ); // Sort descending

  for (const [key, value] of breakpointEntries) {
    if (width >= parseInt(value)) {
      logger.debug("Current breakpoint detected", { breakpoint: key, width });
      return key as Breakpoint;
    }
  }

  // Fallback to smallest breakpoint
  const fallback = "xs";
  logger.debug("Using fallback breakpoint", { breakpoint: fallback, width });
  return fallback;
}
