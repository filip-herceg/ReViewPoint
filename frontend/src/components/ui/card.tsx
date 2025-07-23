import type * as React from "react";

// All classes below use only Tailwind and semantic color variables (no hardcoded colors)

function Card({ className = "", ...props }: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card"
			className={`bg-card text-card-foreground flex flex-col gap-6 rounded-xl border border-card py-6 shadow-sm ${className}`.trim()}
			{...props}
		/>
	);
}

function CardHeader({ className = "", ...props }: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card-header"
			className={`@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6 ${className}`.trim()}
			{...props}
		/>
	);
}

function CardTitle({ className = "", ...props }: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card-title"
			className={`leading-none font-semibold ${className}`.trim()}
			{...props}
		/>
	);
}

function CardDescription({
	className = "",
	...props
}: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card-description"
			className={`text-muted-foreground text-sm ${className}`.trim()}
			{...props}
		/>
	);
}

function CardAction({ className = "", ...props }: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card-action"
			className={`col-start-2 row-span-2 row-start-1 self-start justify-self-end ${className}`.trim()}
			{...props}
		/>
	);
}

function CardContent({
	className = "",
	...props
}: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card-content"
			className={`px-6 ${className}`.trim()}
			{...props}
		/>
	);
}

function CardFooter({ className = "", ...props }: React.ComponentProps<"div">) {
	return (
		<div
			data-slot="card-footer"
			className={`flex items-center px-6 [.border-t]:pt-6 ${className}`.trim()}
			{...props}
		/>
	);
}

export {
	Card,
	CardHeader,
	CardFooter,
	CardTitle,
	CardAction,
	CardDescription,
	CardContent,
};
