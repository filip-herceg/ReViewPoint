/**
 * Design System - Typography Tokens
 * Central typography scale and font definitions for the ReViewPoint design system
 */

import logger from "@/logger";

// Font family definitions
export const fontFamilies = {
	sans: [
		"Inter",
		"-apple-system",
		"BlinkMacSystemFont",
		"Segoe UI",
		"Roboto",
		"Oxygen",
		"Ubuntu",
		"Cantarell",
		"Open Sans",
		"Helvetica Neue",
		"sans-serif",
	],
	mono: [
		"JetBrains Mono",
		"Fira Code",
		"Consolas",
		"Monaco",
		"Courier New",
		"monospace",
	],
} as const;

// Font size scale (in rem)
export const fontSizes = {
	xs: "0.75rem", // 12px
	sm: "0.875rem", // 14px
	base: "1rem", // 16px (base)
	lg: "1.125rem", // 18px
	xl: "1.25rem", // 20px
	"2xl": "1.5rem", // 24px
	"3xl": "1.875rem", // 30px
	"4xl": "2.25rem", // 36px
	"5xl": "3rem", // 48px
	"6xl": "3.75rem", // 60px
	"7xl": "4.5rem", // 72px
	"8xl": "6rem", // 96px
	"9xl": "8rem", // 128px
} as const;

// Font weight scale
export const fontWeights = {
	thin: 100,
	extralight: 200,
	light: 300,
	normal: 400,
	medium: 500,
	semibold: 600,
	bold: 700,
	extrabold: 800,
	black: 900,
} as const;

// Line height scale
export const lineHeights = {
	none: "1",
	tight: "1.25",
	snug: "1.375",
	normal: "1.5",
	relaxed: "1.625",
	loose: "2",
} as const;

// Letter spacing scale
export const letterSpacing = {
	tighter: "-0.05em",
	tight: "-0.025em",
	normal: "0em",
	wide: "0.025em",
	wider: "0.05em",
	widest: "0.1em",
} as const;

// Typography preset combinations
export const typography = {
	// Display headings
	"display-2xl": {
		fontSize: fontSizes["8xl"],
		fontWeight: fontWeights.bold,
		lineHeight: lineHeights.none,
		letterSpacing: letterSpacing.tight,
	},
	"display-xl": {
		fontSize: fontSizes["7xl"],
		fontWeight: fontWeights.bold,
		lineHeight: lineHeights.none,
		letterSpacing: letterSpacing.tight,
	},
	"display-lg": {
		fontSize: fontSizes["6xl"],
		fontWeight: fontWeights.bold,
		lineHeight: lineHeights.none,
		letterSpacing: letterSpacing.tight,
	},
	"display-md": {
		fontSize: fontSizes["5xl"],
		fontWeight: fontWeights.bold,
		lineHeight: lineHeights.tight,
		letterSpacing: letterSpacing.tight,
	},
	"display-sm": {
		fontSize: fontSizes["4xl"],
		fontWeight: fontWeights.bold,
		lineHeight: lineHeights.tight,
		letterSpacing: letterSpacing.normal,
	},
	"display-xs": {
		fontSize: fontSizes["3xl"],
		fontWeight: fontWeights.bold,
		lineHeight: lineHeights.tight,
		letterSpacing: letterSpacing.normal,
	},

	// Text headings
	"text-xl": {
		fontSize: fontSizes["2xl"],
		fontWeight: fontWeights.semibold,
		lineHeight: lineHeights.tight,
		letterSpacing: letterSpacing.normal,
	},
	"text-lg": {
		fontSize: fontSizes.xl,
		fontWeight: fontWeights.semibold,
		lineHeight: lineHeights.tight,
		letterSpacing: letterSpacing.normal,
	},
	"text-md": {
		fontSize: fontSizes.lg,
		fontWeight: fontWeights.semibold,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.normal,
	},
	"text-sm": {
		fontSize: fontSizes.base,
		fontWeight: fontWeights.semibold,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.normal,
	},
	"text-xs": {
		fontSize: fontSizes.sm,
		fontWeight: fontWeights.semibold,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.normal,
	},

	// Body text
	"body-xl": {
		fontSize: fontSizes.xl,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.relaxed,
		letterSpacing: letterSpacing.normal,
	},
	"body-lg": {
		fontSize: fontSizes.lg,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.relaxed,
		letterSpacing: letterSpacing.normal,
	},
	"body-md": {
		fontSize: fontSizes.base,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.normal,
		letterSpacing: letterSpacing.normal,
	},
	"body-sm": {
		fontSize: fontSizes.sm,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.normal,
		letterSpacing: letterSpacing.normal,
	},
	"body-xs": {
		fontSize: fontSizes.xs,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.normal,
		letterSpacing: letterSpacing.normal,
	},

	// Captions and labels
	"caption-lg": {
		fontSize: fontSizes.sm,
		fontWeight: fontWeights.medium,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.wide,
	},
	"caption-md": {
		fontSize: fontSizes.xs,
		fontWeight: fontWeights.medium,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.wide,
	},
	"caption-sm": {
		fontSize: fontSizes.xs,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.wide,
	},

	// Code
	"code-lg": {
		fontSize: fontSizes.base,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.normal,
		letterSpacing: letterSpacing.normal,
		fontFamily: fontFamilies.mono.join(", "),
	},
	"code-md": {
		fontSize: fontSizes.sm,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.normal,
		letterSpacing: letterSpacing.normal,
		fontFamily: fontFamilies.mono.join(", "),
	},
	"code-sm": {
		fontSize: fontSizes.xs,
		fontWeight: fontWeights.normal,
		lineHeight: lineHeights.snug,
		letterSpacing: letterSpacing.normal,
		fontFamily: fontFamilies.mono.join(", "),
	},
} as const;

export type FontFamily = keyof typeof fontFamilies;
export type FontSize = keyof typeof fontSizes;
export type FontWeight = keyof typeof fontWeights;
export type LineHeight = keyof typeof lineHeights;
export type LetterSpacing = keyof typeof letterSpacing;
export type TypographyVariant = keyof typeof typography;

/**
 * Get a typography preset by variant
 */
export function getTypography(variant: TypographyVariant) {
	const preset = typography[variant];
	if (!preset) {
		logger.warn("Invalid typography variant requested", { variant });
		return typography["body-md"]; // Fallback
	}

	logger.debug("Retrieved typography preset", { variant, preset });
	return preset;
}

/**
 * Generate CSS font shorthand
 */
export function getFontShorthand(
	size: FontSize,
	weight: FontWeight = "normal",
	family: FontFamily = "sans",
): string {
	const fontValue = `${fontWeights[weight]} ${fontSizes[size]} ${fontFamilies[family].join(", ")}`;
	logger.debug("Generated font shorthand", {
		size,
		weight,
		family,
		value: fontValue,
	});
	return fontValue;
}
