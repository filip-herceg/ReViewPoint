/**
 * Modal Component - Enhanced modal with animations and accessibility
 * Part of Phase 2.4 UI Design System
 */

import type React from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import logger from "@/logger";

// Modal variant types
export type ModalVariant =
	| "default"
	| "destructive"
	| "warning"
	| "success"
	| "info";

// Modal size types
export type ModalSize = "sm" | "md" | "lg" | "xl" | "full";

// Modal props
export interface ModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	title?: string;
	description?: string;
	children?: React.ReactNode;
	trigger?: React.ReactNode;

	// Actions
	onConfirm?: () => void | Promise<void>;
	onCancel?: () => void;
	confirmText?: string;
	cancelText?: string;
	confirmVariant?: ModalVariant;
	confirmDisabled?: boolean;
	confirmLoading?: boolean;

	// Appearance
	variant?: ModalVariant;
	size?: ModalSize;
	hideFooter?: boolean;
	hideHeader?: boolean;
	hideCloseButton?: boolean;

	// Behavior
	closeOnOverlayClick?: boolean;
	closeOnEscape?: boolean;
	preventClose?: boolean; // Prevent closing when loading/processing

	// Styling
	className?: string;
	headerClassName?: string;
	contentClassName?: string;
	footerClassName?: string;

	// Testing
	testId?: string;
}

// Size configurations
const SIZE_CONFIG: Record<ModalSize, string> = {
	sm: "max-w-md",
	md: "max-w-lg",
	lg: "max-w-2xl",
	xl: "max-w-4xl",
	full: "max-w-[95vw] h-[95vh]",
};

// Variant configurations
const VARIANT_CONFIG: Record<
	ModalVariant,
	{
		headerClass: string;
		confirmButtonVariant: "default" | "destructive" | "outline" | "secondary";
	}
> = {
	default: {
		headerClass: "",
		confirmButtonVariant: "default",
	},
	destructive: {
		headerClass: "text-destructive",
		confirmButtonVariant: "destructive",
	},
	warning: {
		headerClass: "text-warning-foreground", // semantic class
		confirmButtonVariant: "outline",
	},
	success: {
		headerClass: "text-success-foreground", // semantic class
		confirmButtonVariant: "default",
	},
	info: {
		headerClass: "text-info-foreground", // semantic class
		confirmButtonVariant: "default",
	},
};

/**
 * Enhanced Modal component with comprehensive features
 */
export function Modal({
	open,
	onOpenChange,
	title,
	description,
	children,
	trigger,
	onConfirm,
	onCancel,
	confirmText = "Confirm",
	cancelText = "Cancel",
	confirmVariant = "default",
	confirmDisabled = false,
	confirmLoading = false,
	variant = "default",
	size = "md",
	hideFooter = false,
	hideHeader = false,
	hideCloseButton = false,
	closeOnOverlayClick = true,
	closeOnEscape = true,
	preventClose = false,
	className,
	headerClassName,
	contentClassName,
	footerClassName,
	testId = "modal",
}: ModalProps) {
	// Handle confirm action
	const handleConfirm = async () => {
		if (!onConfirm || confirmDisabled || confirmLoading) return;

		try {
			logger.debug("Modal confirm action triggered", { testId, variant });
			await onConfirm();
			// Note: onConfirm should handle closing the modal if needed
		} catch (err) {
			logger.error("Modal confirm action failed", { testId, error: err });
			// Error handling should be done by the parent component
		}
	};

	// Handle cancel action
	const handleCancel = () => {
		if (preventClose) return;

		try {
			logger.debug("Modal cancel action triggered", { testId });
			if (onCancel) {
				onCancel();
			} else {
				onOpenChange(false);
			}
		} catch (err) {
			logger.error("Modal cancel action failed", { testId, error: err });
		}
	};

	// Handle open change with prevention logic
	const handleOpenChange = (newOpen: boolean) => {
		if (!newOpen && preventClose) {
			logger.debug("Modal close prevented", { testId, preventClose });
			return;
		}

		logger.debug("Modal open state changed", { testId, newOpen });
		onOpenChange(newOpen);
	};

	const variantConfig = VARIANT_CONFIG[variant];
	const sizeClass = SIZE_CONFIG[size];

	// Show footer if not hidden and has actions
	const showFooter = !hideFooter && (onConfirm || onCancel);

	return (
		<Dialog open={open} onOpenChange={handleOpenChange} data-testid={testId}>
			{trigger && (
				<DialogTrigger asChild data-testid={`${testId}-trigger`}>
					{trigger}
				</DialogTrigger>
			)}

			<DialogContent
				className={cn(sizeClass, className)}
				onPointerDownOutside={(e) => {
					if (!closeOnOverlayClick || preventClose) {
						e.preventDefault();
					}
				}}
				onEscapeKeyDown={(e) => {
					if (!closeOnEscape || preventClose) {
						e.preventDefault();
					}
				}}
				showCloseButton={!(hideCloseButton || preventClose)}
				data-testid={`${testId}-content`}
			>
				{/* Header */}
				{!hideHeader && (title || description) && (
					<DialogHeader
						className={cn(variantConfig.headerClass, headerClassName)}
						data-testid={`${testId}-header`}
					>
						{title && (
							<DialogTitle data-testid={`${testId}-title`}>{title}</DialogTitle>
						)}
						{description && (
							<DialogDescription data-testid={`${testId}-description`}>
								{description}
							</DialogDescription>
						)}
					</DialogHeader>
				)}

				{/* Content */}
				<div
					className={cn("py-4", contentClassName)}
					data-testid={`${testId}-body`}
				>
					{children}
				</div>

				{/* Footer */}
				{showFooter && (
					<DialogFooter
						className={cn("gap-2", footerClassName)}
						data-testid={`${testId}-footer`}
					>
						{onCancel && (
							<Button
								variant="outline"
								onClick={handleCancel}
								disabled={preventClose}
								data-testid={`${testId}-cancel`}
							>
								{cancelText}
							</Button>
						)}
						{onConfirm && (
							<Button
								variant={variantConfig.confirmButtonVariant}
								onClick={handleConfirm}
								disabled={confirmDisabled || preventClose || confirmLoading}
								data-testid={`${testId}-confirm`}
							>
								{confirmLoading ? "Loading..." : confirmText}
							</Button>
						)}
					</DialogFooter>
				)}
			</DialogContent>
		</Dialog>
	);
}

// Convenience components for common modal types

export interface ConfirmModalProps
	extends Omit<ModalProps, "variant" | "onConfirm"> {
	onConfirm: () => void | Promise<void>;
	message?: string;
}

export function ConfirmModal({
	message,
	title = "Confirm Action",
	confirmText = "Confirm",
	cancelText = "Cancel",
	...props
}: ConfirmModalProps) {
	return (
		<Modal
			{...props}
			variant="default"
			title={title}
			confirmText={confirmText}
			cancelText={cancelText}
		>
			{message && <p>{message}</p>}
		</Modal>
	);
}

export interface DeleteModalProps
	extends Omit<ModalProps, "variant" | "onConfirm"> {
	onConfirm: () => void | Promise<void>;
	itemName?: string;
	message?: string;
}

export function DeleteModal({
	itemName,
	message,
	title,
	confirmText = "Delete",
	cancelText = "Cancel",
	...props
}: DeleteModalProps) {
	const defaultTitle = itemName ? `Delete ${itemName}` : "Delete Item";
	const defaultMessage = itemName
		? `Are you sure you want to delete "${itemName}"? This action cannot be undone.`
		: "Are you sure you want to delete this item? This action cannot be undone.";

	return (
		<Modal
			{...props}
			variant="destructive"
			title={title || defaultTitle}
			confirmText={confirmText}
			cancelText={cancelText}
		>
			<p>{message || defaultMessage}</p>
		</Modal>
	);
}

export interface AlertModalProps
	extends Omit<ModalProps, "variant" | "onCancel" | "onConfirm"> {
	message?: string;
	onClose?: () => void;
}

export function AlertModal({
	message,
	title = "Alert",
	onClose,
	confirmText = "OK",
	...props
}: AlertModalProps) {
	return (
		<Modal
			{...props}
			variant="info"
			title={title}
			confirmText={confirmText}
			onConfirm={onClose || (() => props.onOpenChange(false))}
			hideFooter={false}
		>
			{message && <p>{message}</p>}
		</Modal>
	);
}

export default Modal;
