import type * as React from "react";

// Tailwind-native badge variants (semantic color variables only)
const badgeBase =
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2";

const badgeVariantClasses: Record<string, string> = {
  default:
    "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
  secondary:
    "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
  destructive:
    "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
  success:
    "border-transparent bg-success text-success-foreground shadow hover:bg-success/80",
  warning:
    "border-transparent bg-warning text-warning-foreground shadow hover:bg-warning/80",
  outline: "text-foreground border-border bg-transparent",
};

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: keyof typeof badgeVariantClasses;
}

function Badge({ className = "", variant = "default", ...props }: BadgeProps) {
  const variantClass =
    badgeVariantClasses[variant] || badgeVariantClasses.default;
  return (
    <div
      className={`${badgeBase} ${variantClass} ${className}`.trim()}
      {...props}
    />
  );
}

export { Badge };

// ...existing code...
