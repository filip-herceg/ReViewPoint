import * as React from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface TabsContextType {
	value: string;
	onValueChange: (value: string) => void;
}

const TabsContext = React.createContext<TabsContextType | undefined>(undefined);

const useTabsContext = () => {
	const context = React.useContext(TabsContext);
	if (!context) {
		throw new Error("Tabs components must be used within a Tabs provider");
	}
	return context;
};

interface TabsProps {
	value: string;
	onValueChange: (value: string) => void;
	children: React.ReactNode;
	className?: string;
}

const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
	({ className, value, onValueChange, children, ...props }, ref) => (
		<TabsContext.Provider value={{ value, onValueChange }}>
			<div ref={ref} className={cn("", className)} {...props}>
				{children}
			</div>
		</TabsContext.Provider>
	),
);
Tabs.displayName = "Tabs";

interface TabsListProps {
	children: React.ReactNode;
	className?: string;
}

const TabsList = React.forwardRef<HTMLDivElement, TabsListProps>(
	({ className, children, ...props }, ref) => (
		<div
			ref={ref}
			className={cn(
				"inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground w-full",
				className,
			)}
			{...props}
		>
			{children}
		</div>
	),
);
TabsList.displayName = "TabsList";

interface TabsTriggerProps {
	value: string;
	children: React.ReactNode;
	className?: string;
}

const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(
	({ className, value, children, ...props }, ref) => {
		const { value: selectedValue, onValueChange } = useTabsContext();
		const isActive = selectedValue === value;

		return (
			<Button
				ref={ref}
				variant="ghost"
				className={cn(
					"inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 flex-1",
					isActive
						? "bg-background text-foreground shadow"
						: "hover:bg-muted-foreground/10",
					className,
				)}
				onClick={() => onValueChange(value)}
				{...props}
			>
				{children}
			</Button>
		);
	},
);
TabsTrigger.displayName = "TabsTrigger";

interface TabsContentProps {
	value: string;
	children: React.ReactNode;
	className?: string;
}

const TabsContent = React.forwardRef<HTMLDivElement, TabsContentProps>(
	({ className, value, children, ...props }, ref) => {
		const { value: selectedValue } = useTabsContext();

		if (selectedValue !== value) {
			return null;
		}

		return (
			<div
				ref={ref}
				className={cn(
					"mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
					className,
				)}
				{...props}
			>
				{children}
			</div>
		);
	},
);
TabsContent.displayName = "TabsContent";

export { Tabs, TabsList, TabsTrigger, TabsContent };
