/**
 * Focus Trap Component
 * Traps focus within a container for modals and dialogs
 * Part of Phase 4: Accessibility & Performance Components
 */

import React, { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import logger from "@/logger";

interface FocusTrapProps {
  children: React.ReactNode;
  active?: boolean;
  className?: string;
  restoreFocus?: boolean;
  initialFocus?: HTMLElement | string;
  onEscape?: () => void;
}

/**
 * Get all focusable elements within a container
 */
function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selector = [
    "button:not([disabled])",
    "input:not([disabled])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    "a[href]",
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ].join(", ");

  return Array.from(container.querySelectorAll(selector)) as HTMLElement[];
}

/**
 * Focus Trap Component
 *
 * @example
 * ```tsx
 * <FocusTrap active={isModalOpen} onEscape={() => setIsModalOpen(false)}>
 *   <div>Modal content with focusable elements</div>
 * </FocusTrap>
 * ```
 */
export function FocusTrap({
  children,
  active = true,
  className,
  restoreFocus = true,
  initialFocus,
  onEscape,
}: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!active || !containerRef.current) {
      return;
    }

    const container = containerRef.current;

    // Store previously focused element for restoration
    if (restoreFocus && document.activeElement instanceof HTMLElement) {
      previouslyFocusedElement.current = document.activeElement;
      logger.debug("FocusTrap: Stored previously focused element", {
        element: previouslyFocusedElement.current.tagName,
      });
    }

    // Set initial focus
    const setInitialFocus = () => {
      let elementToFocus: HTMLElement | null = null;

      if (typeof initialFocus === "string") {
        elementToFocus = container.querySelector(initialFocus) as HTMLElement;
      } else if (initialFocus instanceof HTMLElement) {
        elementToFocus = initialFocus;
      }

      if (!elementToFocus) {
        const focusableElements = getFocusableElements(container);
        elementToFocus = focusableElements[0] || container;
      }

      if (elementToFocus) {
        elementToFocus.focus();
        logger.debug("FocusTrap: Set initial focus", {
          element: elementToFocus.tagName,
        });
      }
    };

    // Handle tab navigation
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && onEscape) {
        event.preventDefault();
        logger.info("FocusTrap: Escape key pressed");
        onEscape();
        return;
      }

      if (event.key !== "Tab") {
        return;
      }

      const focusableElements = getFocusableElements(container);
      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement as HTMLElement;

      if (event.shiftKey) {
        // Shift + Tab (backwards)
        if (activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
          logger.debug("FocusTrap: Wrapped to last element");
        }
      } else {
        // Tab (forwards)
        if (activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
          logger.debug("FocusTrap: Wrapped to first element");
        }
      }
    };

    // Set initial focus after a small delay to ensure DOM is ready
    const timer = setTimeout(setInitialFocus, 0);

    // Add event listeners
    document.addEventListener("keydown", handleKeyDown);

    // Cleanup function
    return () => {
      clearTimeout(timer);
      document.removeEventListener("keydown", handleKeyDown);

      // Restore focus
      if (restoreFocus && previouslyFocusedElement.current) {
        previouslyFocusedElement.current.focus();
        logger.debug("FocusTrap: Restored focus to previous element");
      }
    };
  }, [active, initialFocus, onEscape, restoreFocus]);

  if (!active) {
    return <>{children}</>;
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        // Use only Tailwind semantic focus ring and outline classes, no custom color utilities
        "outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        className,
      )}
      tabIndex={-1}
    >
      {children}
    </div>
  );
}

/**
 * Hook for managing focus trap state
 */
export function useFocusTrap() {
  const [isActive, setIsActive] = React.useState(false);

  const activate = React.useCallback(() => {
    setIsActive(true);
    logger.info("FocusTrap: Activated");
  }, []);

  const deactivate = React.useCallback(() => {
    setIsActive(false);
    logger.info("FocusTrap: Deactivated");
  }, []);

  return {
    isActive,
    activate,
    deactivate,
  };
}
