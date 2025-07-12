/**
 * ARIA Live Region Component
 * Provides accessible announcements for dynamic content changes
 * Part of Phase 4: Accessibility & Performance Components
 */

import React, { useEffect, useRef, useState } from "react";
import logger from "@/logger";

type LiveRegionPoliteness = "polite" | "assertive" | "off";

interface AriaLiveRegionProps {
	message?: string;
	politeness?: LiveRegionPoliteness;
	clearDelay?: number;
	className?: string;
	id?: string;
}

/**
 * ARIA Live Region Component
 * Announces dynamic content changes to screen readers
 *
 * @example
 * ```tsx
 * // Polite announcements (default)
 * <AriaLiveRegion message="Form saved successfully" />
 *
 * // Assertive announcements for errors
 * <AriaLiveRegion
 *   message="Error: Please correct the form"
 *   politeness="assertive"
 * />
 * ```
 */
export function AriaLiveRegion({
	message = "",
	politeness = "polite",
	clearDelay = 5000,
	className,
	id = "aria-live-region",
}: AriaLiveRegionProps) {
	const [currentMessage, setCurrentMessage] = useState(message);
	const timeoutRef = useRef<NodeJS.Timeout | null>(null);

	useEffect(() => {
		if (message) {
			setCurrentMessage(message);
			logger.debug("AriaLiveRegion: Announcing message", {
				message,
				politeness,
				clearDelay,
			});

			// Clear message after delay
			if (clearDelay > 0) {
				if (timeoutRef.current) {
					clearTimeout(timeoutRef.current);
				}

				timeoutRef.current = setTimeout(() => {
					setCurrentMessage("");
					logger.debug("AriaLiveRegion: Cleared message after delay");
				}, clearDelay);
			}
		}

		return () => {
			if (timeoutRef.current) {
				clearTimeout(timeoutRef.current);
			}
		};
	}, [message, clearDelay]);

	return (
		<div
			id={id}
			aria-live={politeness}
			aria-atomic="true"
			// Visually hidden but accessible to screen readers
			className={`sr-only text-[color:var(--foreground-muted,inherit)] ${className ? className : ""}`.trim()}
		>
			{currentMessage}
		</div>
	);
}

/**
 * Hook for managing live region announcements
 * Provides a simple API for making announcements
 */
export function useAriaLive(
	defaultPoliteness: LiveRegionPoliteness = "polite",
) {
	const [message, setMessage] = useState("");
	const [politeness, setPoliteness] = useState(defaultPoliteness);

	const announce = React.useCallback(
		(
			newMessage: string,
			newPoliteness: LiveRegionPoliteness = defaultPoliteness,
		) => {
			setMessage(newMessage);
			setPoliteness(newPoliteness);
			logger.info("AriaLive: Making announcement", {
				message: newMessage,
				politeness: newPoliteness,
			});
		},
		[defaultPoliteness],
	);

	const announcePolite = React.useCallback(
		(message: string) => {
			announce(message, "polite");
		},
		[announce],
	);

	const announceAssertive = React.useCallback(
		(message: string) => {
			announce(message, "assertive");
		},
		[announce],
	);

	const clear = React.useCallback(() => {
		setMessage("");
		logger.debug("AriaLive: Cleared message");
	}, []);

	return {
		message,
		politeness,
		announce,
		announcePolite,
		announceAssertive,
		clear,
	};
}

/**
 * Status Announcer Component
 * Specialized live region for status updates
 */
interface StatusAnnouncerProps {
	status?: "loading" | "success" | "error" | "info";
	message?: string;
	className?: string;
}

const STATUS_CONFIG = {
	loading: { politeness: "polite" as const, prefix: "Loading:" },
	success: { politeness: "polite" as const, prefix: "Success:" },
	error: { politeness: "assertive" as const, prefix: "Error:" },
	info: { politeness: "polite" as const, prefix: "Info:" },
};

export function StatusAnnouncer({
	status,
	message = "",
	className,
}: StatusAnnouncerProps) {
	const formattedMessage =
		status && message ? `${STATUS_CONFIG[status].prefix} ${message}` : message;

	const politeness = status ? STATUS_CONFIG[status].politeness : "polite";

	// Use Tailwind semantic color classes for status visually if needed

	// Use only semantic color variables for status
	let statusClass = "";
	if (status === "success") statusClass = "text-success-foreground";
	if (status === "error") statusClass = "text-destructive-foreground";
	if (status === "loading") statusClass = "text-primary-foreground";
	if (status === "info") statusClass = "text-muted-foreground";

	return (
		<AriaLiveRegion
			message={formattedMessage}
			politeness={politeness}
			className={`sr-only ${statusClass} ${className ? className : ""}`.trim()}
			id="status-announcer"
		/>
	);
}

/**
 * Form Validation Announcer
 * Specialized component for form validation messages
 */
interface FormValidationAnnouncerProps {
	errors?: string[];
	fieldName?: string;
	className?: string;
}

export function FormValidationAnnouncer({
	errors = [],
	fieldName,
	className,
}: FormValidationAnnouncerProps) {
	const message = React.useMemo(() => {
		if (errors.length === 0) return "";

		const prefix = fieldName ? `${fieldName} field:` : "Validation error:";
		const errorText =
			errors.length === 1
				? errors[0]
				: `${errors.length} errors: ${errors.join(", ")}`;

		return `${prefix} ${errorText}`;
	}, [errors, fieldName]);

	// Use only semantic color variable for errors
	return (
		<AriaLiveRegion
			message={message}
			politeness="assertive"
			className={`sr-only text-destructive-foreground ${className ? className : ""}`.trim()}
			id={
				fieldName ? `${fieldName}-validation-announcer` : "validation-announcer"
			}
		/>
	);
}

/**
 * Global Live Region Provider
 * Provides app-wide announcement capabilities
 */
interface LiveRegionContextType {
	announce: (message: string, politeness?: LiveRegionPoliteness) => void;
	announceSuccess: (message: string) => void;
	announceError: (message: string) => void;
}

const LiveRegionContext = React.createContext<LiveRegionContextType | null>(
	null,
);

export function LiveRegionProvider({
	children,
}: {
	children: React.ReactNode;
}) {
	const { announce, announcePolite, announceAssertive } = useAriaLive();

	const contextValue = React.useMemo(
		() => ({
			announce,
			announceSuccess: announcePolite,
			announceError: announceAssertive,
		}),
		[announce, announcePolite, announceAssertive],
	);

	return (
		<LiveRegionContext.Provider value={contextValue}>
			{children}
			{/* Global live region, visually hidden, Tailwind only */}
			<AriaLiveRegion
				id="global-live-region"
				className="sr-only text-muted-foreground"
			/>
		</LiveRegionContext.Provider>
	);
}

/**
 * Hook to access global live region context
 */
export function useLiveRegion() {
	const context = React.useContext(LiveRegionContext);
	if (!context) {
		throw new Error("useLiveRegion must be used within a LiveRegionProvider");
	}
	return context;
}
