"use client";

import { useTheme } from "next-themes";
import { Toaster as Sonner, type ToasterProps } from "sonner";

const Toaster = ({ ...props }: ToasterProps) => {
	const { theme = "system" } = useTheme();

	return (
		<Sonner
			theme={theme as ToasterProps["theme"]}
			className="toaster group bg-popover text-popover-foreground border border-border"
			// No inline style overrides; use only Tailwind semantic color classes
			{...props}
		/>
	);
};

export { Toaster };
