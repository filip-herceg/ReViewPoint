/** @type {import('tailwindcss').Config} */
export default {
	darkMode: ["class"],
	content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
	theme: {
		extend: {
			borderRadius: {
				lg: "var(--radius)",
				md: "calc(var(--radius) - 2px)",
				sm: "calc(var(--radius) - 4px)",
			},
			colors: {
				background: "hsl(var(--background))",
				foreground: "hsl(var(--foreground))",
				card: {
					DEFAULT: "hsl(var(--card))",
					foreground: "hsl(var(--card-foreground))",
				},
				popover: {
					DEFAULT: "hsl(var(--popover))",
					foreground: "hsl(var(--popover-foreground))",
				},
				primary: {
					DEFAULT: "hsl(var(--primary))",
					foreground: "hsl(var(--primary-foreground))",
				},
				secondary: {
					DEFAULT: "hsl(var(--secondary))",
					foreground: "hsl(var(--secondary-foreground))",
				},
				muted: {
					DEFAULT: "hsl(var(--muted))",
					foreground: "hsl(var(--muted-foreground))",
				},
				accent: {
					DEFAULT: "hsl(var(--accent))",
					foreground: "hsl(var(--accent-foreground))",
				},
				destructive: {
					DEFAULT: "hsl(var(--destructive))",
					foreground: "hsl(var(--destructive-foreground))",
				},
				// === Semantic Colors for Full Compliance with index.css ===
				success: {
					DEFAULT: "hsl(var(--color-success))",
					foreground: "hsl(var(--color-success-foreground))",
				},
				warning: {
					DEFAULT: "hsl(var(--color-warning))",
					foreground: "hsl(var(--color-warning-foreground))",
				},
				error: {
					DEFAULT: "hsl(var(--color-error))",
					foreground: "hsl(var(--color-error-foreground))",
				},
				info: {
					DEFAULT: "hsl(var(--color-info))",
					foreground: "hsl(var(--color-info-foreground))",
				},
				// === End Semantic Colors ===
				border: "hsl(var(--border))",
				input: "hsl(var(--input))",
				ring: "hsl(var(--ring))",
				sidebar: {
					DEFAULT: "hsl(var(--sidebar))",
					foreground: "hsl(var(--sidebar-foreground))",
					primary: "hsl(var(--sidebar-primary))",
					"primary-foreground": "hsl(var(--sidebar-primary-foreground))",
					accent: "hsl(var(--sidebar-accent))",
					"accent-foreground": "hsl(var(--sidebar-accent-foreground))",
					border: "hsl(var(--sidebar-border))",
					ring: "hsl(var(--sidebar-ring))",
				},
				chart: {
					1: "hsl(var(--chart-1))",
					2: "hsl(var(--chart-2))",
					3: "hsl(var(--chart-3))",
					4: "hsl(var(--chart-4))",
					5: "hsl(var(--chart-5))",
				},
			},
			spacing: {
				0: "var(--space-0)",
				1: "var(--space-1)",
				2: "var(--space-2)",
				3: "var(--space-3)",
				4: "var(--space-4)",
				6: "var(--space-6)",
				8: "var(--space-8)",
				12: "var(--space-12)",
				16: "var(--space-16)",
				20: "var(--space-20)",
				24: "var(--space-24)",
				32: "var(--space-32)",
			},
			fontSize: {
				xs: "var(--font-size-xs)",
				sm: "var(--font-size-sm)",
				base: "var(--font-size-base)",
				lg: "var(--font-size-lg)",
				xl: "var(--font-size-xl)",
				"2xl": "var(--font-size-2xl)",
				"3xl": "var(--font-size-3xl)",
				"4xl": "var(--font-size-4xl)",
			},
			animation: {
				"accordion-down": "accordion-down 0.2s ease-out",
				"accordion-up": "accordion-up 0.2s ease-out",
				"fade-in": "fade-in 0.5s ease-out",
				"slide-up": "slide-up 0.3s ease-out",
				"bounce-subtle": "bounce-subtle 2s infinite",
			},
			keyframes: {
				"accordion-down": {
					from: { height: "0" },
					to: { height: "var(--radix-accordion-content-height)" },
				},
				"accordion-up": {
					from: { height: "var(--radix-accordion-content-height)" },
					to: { height: "0" },
				},
				"fade-in": {
					"0%": { opacity: "0", transform: "translateY(10px)" },
					"100%": { opacity: "1", transform: "translateY(0)" },
				},
				"slide-up": {
					"0%": { opacity: "0", transform: "translateY(20px)" },
					"100%": { opacity: "1", transform: "translateY(0)" },
				},
				"bounce-subtle": {
					"0%, 20%, 50%, 80%, 100%": { transform: "translateY(0)" },
					"40%": { transform: "translateY(-5px)" },
					"60%": { transform: "translateY(-3px)" },
				},
			},
			backgroundImage: {
				"gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
				"gradient-conic":
					"conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
			},
			boxShadow: {
				elegant: "0 4px 20px -2px rgba(0, 0, 0, 0.1)",
				"elegant-lg": "0 8px 40px -4px rgba(0, 0, 0, 0.12)",
			},
		},
	},
	plugins: [require("tailwindcss-animate")],
};
