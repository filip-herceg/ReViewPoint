/**
 * Toast Component - Enhanced toast notifications using Sonner
 * Part of Phase 2.4 UI Design System
 */

import { AlertCircle, CheckCircle, Info, XCircle } from "lucide-react";
import { Toaster, type ToasterProps, toast } from "sonner";
import { cn } from "@/lib/utils";
import logger from "@/logger";

// Toast types matching our design system
export type ToastType = "success" | "error" | "warning" | "info" | "loading";

// Enhanced toast options
export interface ToastOptions {
	description?: string;
	duration?: number;
	onDismiss?: () => void;
	dismissible?: boolean;
	id?: string | number;
	closeButton?: boolean;
}

// Icon mapping for different toast types
const TOAST_ICONS = {
	success: CheckCircle,
	error: XCircle,
	warning: AlertCircle,
	info: Info,
};

// Default toast configurations
const DEFAULT_DURATION = 4000;
const LONG_DURATION = 8000;

/**
 * Enhanced toast helper functions
 */
export const showToast = {
	/**
	 * Show success toast
	 */
	success: (message: string, options: ToastOptions = {}) => {
		logger.info("Success toast shown", { message, options });

		const SuccessIcon = TOAST_ICONS.success;
		return toast.success(message, {
			duration: options.duration || DEFAULT_DURATION,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible ?? true,
			id: options.id,
			closeButton: options.closeButton,
			icon: <SuccessIcon className="size-4" />,
		});
	},

	/**
	 * Show error toast
	 */
	error: (message: string, options: ToastOptions = {}) => {
		logger.error("Error toast shown", { message, options });

		const ErrorIcon = TOAST_ICONS.error;
		return toast.error(message, {
			duration: options.duration || LONG_DURATION,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible ?? true,
			id: options.id,
			closeButton: options.closeButton ?? true,
			icon: <ErrorIcon className="size-4" />,
		});
	},

	/**
	 * Show warning toast
	 */
	warning: (message: string, options: ToastOptions = {}) => {
		logger.warn("Warning toast shown", { message, options });

		const WarningIcon = TOAST_ICONS.warning;
		return toast.warning(message, {
			duration: options.duration || LONG_DURATION,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible ?? true,
			id: options.id,
			closeButton: options.closeButton,
			icon: <WarningIcon className="size-4" />,
		});
	},

	/**
	 * Show info toast
	 */
	info: (message: string, options: ToastOptions = {}) => {
		logger.info("Info toast shown", { message, options });

		const InfoIcon = TOAST_ICONS.info;
		return toast.info(message, {
			duration: options.duration || DEFAULT_DURATION,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible ?? true,
			id: options.id,
			closeButton: options.closeButton,
			icon: <InfoIcon className="size-4" />,
		});
	},

	/**
	 * Show loading toast
	 */
	loading: (message: string, options: ToastOptions = {}) => {
		logger.info("Loading toast shown", { message, options });

		return toast.loading(message, {
			duration: options.duration || Infinity,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible ?? false,
			id: options.id,
			closeButton: options.closeButton,
		});
	},

	/**
	 * Show custom toast
	 */
	custom: (
		message: string,
		options: ToastOptions & { icon?: React.ReactNode } = {},
	) => {
		logger.info("Custom toast shown", { message, options });

		return toast(message, {
			duration: options.duration || DEFAULT_DURATION,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible ?? true,
			id: options.id,
			closeButton: options.closeButton,
			icon: options.icon,
		});
	},

	/**
	 * Show promise-based toast (for async operations)
	 */
	promise: <T,>(
		promise: Promise<T>,
		messages: {
			loading: string;
			success: string | ((data: T) => string);
			error: string | ((error: any) => string);
		},
		options: ToastOptions = {},
	) => {
		logger.info("Promise toast started", { messages, options });

		return toast.promise(promise, {
			loading: messages.loading,
			success: messages.success,
			error: messages.error,
			duration: options.duration,
			description: options.description,
			onDismiss: options.onDismiss,
			dismissible: options.dismissible,
			id: options.id,
			closeButton: options.closeButton,
		});
	},

	/**
	 * Dismiss specific toast
	 */
	dismiss: (id?: string | number) => {
		logger.debug("Toast dismissed", { id });
		return toast.dismiss(id);
	},

	/**
	 * Dismiss all toasts
	 */
	dismissAll: () => {
		logger.debug("All toasts dismissed");
		return toast.dismiss();
	},
};

// Enhanced Toaster component with proper theming
export interface ToasterConfig extends Omit<ToasterProps, "theme"> {
	theme?: "light" | "dark" | "system";
}

export function ToastProvider({
	position = "top-right",
	theme = "system",
	richColors = true,
	closeButton = true,
	duration = DEFAULT_DURATION,
	visibleToasts = 5,
	expand = true,
	gap = 14,
	offset = 32,
	className,
	toastOptions,
	...props
}: ToasterConfig = {}) {
	return (
		<Toaster
			position={position}
			theme={theme}
			richColors={richColors}
			closeButton={closeButton}
			duration={duration}
			visibleToasts={visibleToasts}
			expand={expand}
			gap={gap}
			offset={offset}
			className={cn(
				// Use only Tailwind semantic color classes for all toast backgrounds, borders, and text
				"[&_[data-sonner-toaster]]:bg-background",
				"[&_[data-sonner-toast]]:bg-background",
				"[&_[data-sonner-toast]]:border-border",
				"[&_[data-sonner-toast]]:text-foreground",
				"[&_[data-sonner-toast][data-styled=true]]:bg-background",
				"[&_[data-sonner-toast][data-styled=true]]:border-border",
				className,
			)}
			toastOptions={{
				classNames: {
					toast: cn(
						"group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg",
					),
					description: "group-[.toast]:text-muted-foreground",
					actionButton:
						"group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
					cancelButton:
						"group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
					closeButton:
						"group-[.toast]:border-border group-[.toast]:bg-background group-[.toast]:text-foreground",
					success:
						"group-[.toast]:bg-background group-[.toast]:text-foreground group-[.toast]:border-success",
					error:
						"group-[.toast]:bg-background group-[.toast]:text-foreground group-[.toast]:border-destructive",
					warning:
						"group-[.toast]:bg-background group-[.toast]:text-foreground group-[.toast]:border-warning",
					info: "group-[.toast]:bg-background group-[.toast]:text-foreground group-[.toast]:border-info",
				},
				...toastOptions,
			}}
			{...props}
		/>
	);
}

// Convenience hooks for common use cases
export const useToast = () => {
	return {
		toast: showToast,
		dismiss: showToast.dismiss,
		dismissAll: showToast.dismissAll,
	};
};

// Export everything
export { toast as sonnerToast, Toaster };
export default showToast;
