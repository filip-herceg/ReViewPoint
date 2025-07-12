import * as React from "react";

// Tailwind-native, semantic color variables only
const alertBase =
	"relative w-full rounded-lg border px-4 py-3 text-sm [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground [&>svg~*]:pl-7";

const alertVariantClasses: Record<string, string> = {
	default: "bg-background text-foreground border-border",
	destructive:
		"bg-destructive/10 text-destructive-foreground border-destructive [&>svg]:text-destructive-foreground",
	warning:
		"bg-warning/10 text-warning-foreground border-warning [&>svg]:text-warning-foreground",
	success:
		"bg-success/10 text-success-foreground border-success [&>svg]:text-success-foreground",
};

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
	variant?: keyof typeof alertVariantClasses;
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
	({ className = "", variant = "default", ...props }, ref) => {
		const variantClass =
			alertVariantClasses[variant] || alertVariantClasses.default;
		return (
			<div
				ref={ref}
				role="alert"
				className={[alertBase, variantClass, className]
					.filter(Boolean)
					.join(" ")}
				{...props}
			/>
		);
	},
);
Alert.displayName = "Alert";

const AlertTitle = React.forwardRef<
	HTMLHeadingElement,
	React.HTMLAttributes<HTMLHeadingElement>
>(({ className = "", ...props }, ref) => (
	<h5
		ref={ref}
		className={["mb-1 font-medium leading-none tracking-tight", className]
			.filter(Boolean)
			.join(" ")}
		{...props}
	/>
));
AlertTitle.displayName = "AlertTitle";

const AlertDescription = React.forwardRef<
	HTMLParagraphElement,
	React.HTMLAttributes<HTMLParagraphElement>
>(({ className = "", ...props }, ref) => (
	<div
		ref={ref}
		className={["text-sm [&_p]:leading-relaxed", className]
			.filter(Boolean)
			.join(" ")}
		{...props}
	/>
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertTitle, AlertDescription };
