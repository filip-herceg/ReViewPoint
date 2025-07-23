/**
 * Button Debug Utilities
 * Helper functions to debug React.Children.only issues with Button asChild
 */

import React from "react";

/**
 * Debug helper to analyze children structure for Button asChild
 */
export function debugButtonChildren(
  children: React.ReactNode,
  componentName = "Button",
) {
  console.group(`🔍 ${componentName} asChild Debug`);

  console.log("Raw children:", children);
  console.log("Children type:", typeof children);
  console.log("Is valid element:", React.isValidElement(children));

  if (children === null || children === undefined) {
    console.warn("❌ No children provided");
    console.groupEnd();
    return false;
  }

  const childCount = React.Children.count(children);
  console.log("Child count:", childCount);

  if (childCount === 0) {
    console.warn("❌ No valid children found");
    console.groupEnd();
    return false;
  }

  if (childCount > 1) {
    console.warn(
      "❌ Multiple children detected. React.Children.only will fail.",
    );
    console.log("Children list:");
    React.Children.forEach(children, (child, index) => {
      console.log(`  [${index}]:`, child);
    });
    console.groupEnd();
    return false;
  }

  const child = React.Children.only(children);
  console.log("✅ Single child detected:", child);

  if (React.isValidElement(child)) {
    console.log("Child type:", child.type);
    console.log("Child props:", child.props);

    // Check if child has its own children
    const childProps = child.props as Record<string, unknown>;
    if (childProps.children) {
      const grandChildCount = React.Children.count(childProps.children);
      console.log("Grand-child count:", grandChildCount);

      if (grandChildCount > 0) {
        console.log("Grand-children:");
        React.Children.forEach(childProps.children, (grandChild, index) => {
          console.log(`  [${index}]:`, grandChild);
        });
      }
    }
  }

  console.groupEnd();
  return true;
}

/**
 * Enhanced Button component with debugging for development
 */
export function DebugButton({
  children,
  asChild,
  debug = false,
  ...props
}: {
  children: React.ReactNode;
  asChild?: boolean;
  debug?: boolean;
} & Record<string, unknown>) {
  if (debug && asChild) {
    debugButtonChildren(children, "DebugButton");
  }

  // Import actual Button component dynamically to avoid circular deps
  const { Button } = require("@/components/ui/button");

  return (
    <Button asChild={asChild} {...props}>
      {children}
    </Button>
  );
}

/**
 * Validate asChild usage at runtime
 */
export function validateAsChildUsage(children: React.ReactNode): {
  isValid: boolean;
  error?: string;
  suggestion?: string;
} {
  if (!children) {
    return {
      isValid: false,
      error: "No children provided to Button with asChild",
      suggestion: "Provide exactly one React element as a child",
    };
  }

  const childCount = React.Children.count(children);

  if (childCount === 0) {
    return {
      isValid: false,
      error: "No valid children found",
      suggestion: "Provide exactly one React element as a child",
    };
  }

  if (childCount > 1) {
    return {
      isValid: false,
      error: `Expected 1 child, got ${childCount}`,
      suggestion:
        "Wrap multiple elements in a single container element (e.g., <div> or <span>)",
    };
  }

  try {
    const child = React.Children.only(children);
    if (!React.isValidElement(child)) {
      return {
        isValid: false,
        error: "Child is not a valid React element",
        suggestion: "Ensure the child is a proper React component or element",
      };
    }
  } catch (error) {
    return {
      isValid: false,
      error: `React.Children.only failed: ${error}`,
      suggestion: "Check that you have exactly one React element child",
    };
  }

  return { isValid: true };
}

/**
 * Development-only component to wrap problematic Button usages
 */
export function SafeButtonAsChild({
  children,
  fallback,
  ...buttonProps
}: {
  children: React.ReactNode;
  fallback?: React.ReactNode;
} & Record<string, unknown>) {
  const validation = validateAsChildUsage(children);

  if (!validation.isValid) {
    console.error("SafeButtonAsChild validation failed:", validation.error);
    console.log("Suggestion:", validation.suggestion);

    if (fallback) {
      return <>{fallback}</>;
    }

    // Fallback to regular button
    const { Button } = require("@/components/ui/button");
    return (
      <Button {...buttonProps}>
        {typeof children === "string" ? children : "Button"}
      </Button>
    );
  }

  const { Button } = require("@/components/ui/button");
  return (
    <Button asChild {...buttonProps}>
      {children}
    </Button>
  );
}

// Development helper to find all Button asChild usages in a component tree
export function findButtonAsChildUsages(_component: React.ComponentType) {
  // This would need to be implemented with React DevTools or testing utilities
  console.warn(
    "findButtonAsChildUsages: Not implemented - use React DevTools to inspect component tree",
  );
}
