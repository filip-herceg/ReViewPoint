import * as React from "react"
import { Slot } from "@radix-ui/react-slot"

// Tailwind-native button base and variants (semantic color variables only)
const buttonBase = "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 outline-none focus-visible:border-primary focus-visible:ring-primary/50 focus-visible:ring-2 focus-visible:ring-offset-2";

const buttonVariantClasses: Record<string, string> = {
  default: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
  destructive: "bg-destructive text-destructive-foreground shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
  outline: "border border-border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50",
  secondary: "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
  ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
  link: "text-primary underline-offset-4 hover:underline bg-transparent shadow-none",
};

const buttonSizeClasses: Record<string, string> = {
  default: "h-9 px-4 py-2",
  sm: "h-8 rounded-md gap-1.5 px-3 py-1.5 text-sm",
  lg: "h-10 rounded-md px-6 py-2.5 text-base",
  icon: "size-9 p-0",
};

export interface ButtonProps extends React.ComponentProps<"button"> {
  variant?: keyof typeof buttonVariantClasses;
  size?: keyof typeof buttonSizeClasses;
  asChild?: boolean;
}

function Button({
  className = '',
  variant = 'default',
  size = 'default',
  asChild = false,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  const variantClass = buttonVariantClasses[variant] || buttonVariantClasses.default;
  const sizeClass = buttonSizeClasses[size] || buttonSizeClasses.default;
  return (
    <Comp
      data-slot="button"
      className={[buttonBase, variantClass, sizeClass, className].filter(Boolean).join(' ')}
      {...props}
    />
  );
}

export { Button };

// ...existing code...
