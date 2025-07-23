/**
 * Design System - Spacing Tokens
 * Central spacing scale for consistent layout and component spacing
 */

import logger from "@/logger";

// Base spacing scale (in rem)
export const spacing = {
  0: "0rem",
  0.5: "0.125rem", // 2px
  1: "0.25rem", // 4px
  1.5: "0.375rem", // 6px
  2: "0.5rem", // 8px
  2.5: "0.625rem", // 10px
  3: "0.75rem", // 12px
  3.5: "0.875rem", // 14px
  4: "1rem", // 16px
  5: "1.25rem", // 20px
  6: "1.5rem", // 24px
  7: "1.75rem", // 28px
  8: "2rem", // 32px
  9: "2.25rem", // 36px
  10: "2.5rem", // 40px
  11: "2.75rem", // 44px
  12: "3rem", // 48px
  14: "3.5rem", // 56px
  16: "4rem", // 64px
  20: "5rem", // 80px
  24: "6rem", // 96px
  28: "7rem", // 112px
  32: "8rem", // 128px
  36: "9rem", // 144px
  40: "10rem", // 160px
  44: "11rem", // 176px
  48: "12rem", // 192px
  52: "13rem", // 208px
  56: "14rem", // 224px
  60: "15rem", // 240px
  64: "16rem", // 256px
  72: "18rem", // 288px
  80: "20rem", // 320px
  96: "24rem", // 384px
} as const;

// Semantic spacing for specific use cases
export const semanticSpacing = {
  // Component spacing
  componentXs: spacing[1], // 4px - Minimal spacing within components
  componentSm: spacing[2], // 8px - Small component spacing
  componentMd: spacing[4], // 16px - Default component spacing
  componentLg: spacing[6], // 24px - Large component spacing
  componentXl: spacing[8], // 32px - Extra large component spacing

  // Layout spacing
  layoutXs: spacing[4], // 16px - Minimal layout spacing
  layoutSm: spacing[6], // 24px - Small layout spacing
  layoutMd: spacing[8], // 32px - Default layout spacing
  layoutLg: spacing[12], // 48px - Large layout spacing
  layoutXl: spacing[16], // 64px - Extra large layout spacing
  layoutXxl: spacing[24], // 96px - XXL layout spacing

  // Section spacing
  sectionXs: spacing[8], // 32px - Minimal section spacing
  sectionSm: spacing[12], // 48px - Small section spacing
  sectionMd: spacing[16], // 64px - Default section spacing
  sectionLg: spacing[24], // 96px - Large section spacing
  sectionXl: spacing[32], // 128px - Extra large section spacing

  // Container spacing
  containerXs: spacing[4], // 16px - Minimal container padding
  containerSm: spacing[6], // 24px - Small container padding
  containerMd: spacing[8], // 32px - Default container padding
  containerLg: spacing[12], // 48px - Large container padding
  containerXl: spacing[16], // 64px - Extra large container padding
} as const;

// Border radius scale
export const borderRadius = {
  none: "0rem",
  sm: "0.125rem", // 2px
  default: "0.25rem", // 4px
  md: "0.375rem", // 6px
  lg: "0.5rem", // 8px
  xl: "0.75rem", // 12px
  "2xl": "1rem", // 16px
  "3xl": "1.5rem", // 24px
  full: "9999px", // Fully rounded
} as const;

// Shadow scale
export const shadows = {
  none: "none",
  sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
  default: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
  "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
  inner: "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
} as const;

export type SpacingValue = keyof typeof spacing;
export type SemanticSpacingValue = keyof typeof semanticSpacing;
export type BorderRadiusValue = keyof typeof borderRadius;
export type ShadowValue = keyof typeof shadows;

/**
 * Get spacing value by key
 */
export function getSpacing(value: SpacingValue): string {
  const spacingValue = spacing[value];
  if (!spacingValue) {
    logger.warn("Invalid spacing value requested", { value });
    return spacing[4]; // Fallback to 16px
  }

  logger.debug("Retrieved spacing value", { value, spacingValue });
  return spacingValue;
}

/**
 * Get semantic spacing value by key
 */
export function getSemanticSpacing(value: SemanticSpacingValue): string {
  const spacingValue = semanticSpacing[value];
  if (!spacingValue) {
    logger.warn("Invalid semantic spacing value requested", { value });
    return semanticSpacing.componentMd; // Fallback
  }

  logger.debug("Retrieved semantic spacing value", { value, spacingValue });
  return spacingValue;
}

/**
 * Get border radius value by key
 */
export function getBorderRadius(value: BorderRadiusValue): string {
  const radiusValue = borderRadius[value];
  if (!radiusValue) {
    logger.warn("Invalid border radius value requested", { value });
    return borderRadius.default; // Fallback
  }

  logger.debug("Retrieved border radius value", { value, radiusValue });
  return radiusValue;
}

/**
 * Get shadow value by key
 */
export function getShadow(value: ShadowValue): string {
  const shadowValue = shadows[value];
  if (!shadowValue) {
    logger.warn("Invalid shadow value requested", { value });
    return shadows.default; // Fallback
  }

  logger.debug("Retrieved shadow value", { value, shadowValue });
  return shadowValue;
}
