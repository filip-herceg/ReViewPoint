import * as React from "react";
import { cn } from "@/lib/utils";

// Tailwind-native button base and variants (semantic color variables only)
const buttonBase =
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 outline-none focus-visible:border-primary focus-visible:ring-primary/50 focus-visible:ring-2 focus-visible:ring-offset-2";

const buttonVariantClasses: Record<string, string> = {
  default: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
  destructive:
    "bg-destructive text-[var(--destructive-foreground)] shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
  outline:
    "border border-border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50",
  "outline-destructive":
    "border border-destructive text-destructive bg-background shadow-xs hover:bg-destructive/10 focus-visible:ring-destructive/20",
  "outline-success":
    "border border-[var(--color-success)] text-[var(--color-success)] bg-background shadow-xs hover:bg-[var(--color-success)]/10 focus-visible:ring-[var(--color-success)]/20",
  secondary:
    "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
  ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
  link: "text-primary underline-offset-4 hover:underline bg-transparent shadow-none",
  "icon-sm":
    "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50 focus:outline-none",
  tab: "w-full flex items-center gap-3 px-3 py-2 text-left rounded-md transition-colors hover:bg-muted data-[active=true]:bg-primary/10 data-[active=true]:text-primary",
  "theme-option":
    "p-3 border rounded-lg flex flex-col items-center gap-2 transition-colors border-border hover:bg-muted data-[active=true]:border-primary data-[active=true]:bg-primary/10",
  "floating-icon":
    "absolute bg-primary text-[var(--text-inverse)] rounded-full hover:opacity-90 transition-all shadow-md",
};

const buttonSizeClasses: Record<string, string> = {
  default: "h-9 px-4 py-2",
  sm: "h-8 rounded-md gap-1.5 px-3 py-1.5 text-sm",
  lg: "h-10 rounded-md px-6 py-2.5 text-base",
  icon: "size-9 p-0",
  "icon-sm": "size-6 p-0",
  floating: "p-2",
  none: "p-0", // For special cases where variant handles all sizing
};

export interface ButtonProps extends React.ComponentProps<"button"> {
  variant?: keyof typeof buttonVariantClasses;
  size?: keyof typeof buttonSizeClasses;
  asChild?: boolean;
  active?: boolean;
  loading?: boolean;
}

function Button({
  className = "",
  variant = "default",
  size = "default",
  asChild = false,
  active = false,
  loading = false,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const variantClass =
    buttonVariantClasses[variant] || buttonVariantClasses.default;
  const sizeClass = buttonSizeClasses[size] || buttonSizeClasses.default;

  const combinedClassName = cn(buttonBase, variantClass, sizeClass, className);

  // If asChild is true, clone the first child and merge props
  if (asChild) {
    if (!children) {
      if (process.env.NODE_ENV === "development") {
        console.warn("Button: asChild prop requires children to be provided");
      }
      return null;
    }

    // Convert children to array and get the first element
    const childArray = React.Children.toArray(children);
    const firstChild = childArray[0];

    if (!React.isValidElement(firstChild)) {
      if (process.env.NODE_ENV === "development") {
        console.warn(
          "Button: asChild prop requires the first child to be a React element",
        );
      }
      return null;
    }

    // Type the child as ReactElement with props interface
    const typedChild = firstChild as React.ReactElement<{
      className?: string;
      [key: string]: unknown;
    }>;

    // Clone the first child element with merged props
    return React.cloneElement(typedChild, {
      ...typedChild.props,
      ...props,
      className: cn(typedChild.props?.className, combinedClassName),
      "data-slot": "button",
      "data-active": active,
      disabled: disabled || loading,
    });
  }

  // Regular button rendering
  return (
    <button
      data-slot="button"
      data-active={active}
      disabled={disabled || loading}
      className={combinedClassName}
      {...props}
    >
      {loading && (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
      )}
      {children}
    </button>
  );
}

export { Button };
