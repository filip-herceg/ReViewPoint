/**
 * Theme Toggle Component
 * Provides UI for switching between light and dark themes
 */

import React from "react";
import { Moon, Sun, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme, useSystemTheme } from "@/lib/theme/theme-provider";
import { cn } from "@/lib/utils";
import logger from "@/logger";

interface ThemeToggleProps {
  variant?: "icon" | "text" | "dropdown";
  size?: "sm" | "default" | "lg";
  className?: string;
}

/**
 * Simple icon-based theme toggle
 */
export function ThemeToggle({
  variant = "icon",
  size = "default",
  className,
}: ThemeToggleProps) {
  const { mode, toggleMode } = useTheme();

  const handleToggle = () => {
    logger.info("Theme toggle clicked", { currentMode: mode });
    toggleMode();
  };

  if (variant === "dropdown") {
    return <ThemeToggleDropdown className={className} size={size} />;
  }

  if (variant === "text") {
    return (
      <Button
        variant="outline"
        size={size}
        onClick={handleToggle}
        className={cn("gap-2", className)}
        aria-label={`Switch to ${mode === "light" ? "dark" : "light"} theme`}
      >
        {mode === "light" ? (
          <>
            <Moon className="h-4 w-4" />
            <span>Dark Mode</span>
          </>
        ) : (
          <>
            <Sun className="h-4 w-4" />
            <span>Light Mode</span>
          </>
        )}
      </Button>
    );
  }

  // Default icon variant
  return (
    <Button
      variant="outline"
      size={size}
      onClick={handleToggle}
      className={cn("px-3", className)}
      aria-label={`Switch to ${mode === "light" ? "dark" : "light"} theme`}
    >
      {mode === "light" ? (
        <Moon className="h-4 w-4" />
      ) : (
        <Sun className="h-4 w-4" />
      )}
    </Button>
  );
}

/**
 * Dropdown-based theme toggle with system option
 */
export function ThemeToggleDropdown({
  className,
  size = "default",
}: Pick<ThemeToggleProps, "className" | "size">) {
  const { mode, setMode } = useTheme();
  const systemTheme = useSystemTheme();

  const handleThemeChange = (newMode: "light" | "dark" | "system") => {
    logger.info("Theme changed via dropdown", { from: mode, to: newMode });

    if (newMode === "system") {
      setMode(systemTheme);
      // Note: In a full implementation, you might want to store 'system'
      // as a separate state and watch for system changes
    } else {
      setMode(newMode);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size={size}
          className={cn("px-3", className)}
          aria-label="Theme options"
        >
          {mode === "light" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          onClick={() => handleThemeChange("light")}
          className="gap-2"
        >
          <Sun className="h-4 w-4" />
          <span>Light</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => handleThemeChange("dark")}
          className="gap-2"
        >
          <Moon className="h-4 w-4" />
          <span>Dark</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => handleThemeChange("system")}
          className="gap-2"
        >
          <Monitor className="h-4 w-4" />
          <span>System</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Compact theme toggle for use in navigation or toolbars
 */
export function ThemeToggleCompact({ className }: { className?: string }) {
  const { mode, toggleMode } = useTheme();

  return (
    <button
      onClick={toggleMode}
      className={cn(
        // Use only Tailwind semantic color classes for all states
        "inline-flex items-center justify-center rounded-md p-2",
        "text-sm font-medium transition-colors",
        "bg-background text-foreground",
        "hover:bg-accent hover:text-accent-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        "disabled:pointer-events-none disabled:opacity-50",
        className,
      )}
      aria-label={`Switch to ${mode === "light" ? "dark" : "light"} theme`}
    >
      {mode === "light" ? (
        <Moon className="h-4 w-4" />
      ) : (
        <Sun className="h-4 w-4" />
      )}
    </button>
  );
}
