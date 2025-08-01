import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export interface SkeletonLoaderProps {
	/** Type of skeleton to render */
	variant?: "text" | "circular" | "rectangular" | "card" | "table" | "list";
	/** Number of skeleton items to render */
	count?: number;
	/** Height of the skeleton */
	height?: string | number;
	/** Width of the skeleton */
	width?: string | number;
	/** Additional CSS classes */
	className?: string;
	/** Test ID for testing */
	testId?: string;
	/** Animation type */
	animation?: "pulse" | "wave" | "none";
}

/**
 * SkeletonLoader component provides consistent loading states
 * Supports various skeleton types and configurations
 */
export function SkeletonLoader({
	variant = "text",
	count = 1,
	height,
	width,
	className,
	testId = "skeleton-loader",
	animation = "pulse",
}: SkeletonLoaderProps) {
	const animationClasses = {
		pulse: "animate-pulse",
		wave: "animate-pulse", // Could be enhanced with wave animation
		none: "",
	};

	const renderSkeleton = (index: number) => {
		const key = `skeleton-${index}`;
		const itemTestId = count > 1 ? `${testId}-item-${index}` : testId;

		// All skeletons use only Tailwind semantic color classes for background and border
		switch (variant) {
			case "circular":
				return (
					<Skeleton
						key={key}
						className={cn(
							"rounded-full bg-muted",
							animationClasses[animation],
							className,
						)}
						style={{
							height: height || "40px",
							width: width || "40px",
						}}
						data-testid={itemTestId}
					/>
				);

			case "rectangular":
				return (
					<Skeleton
						key={key}
						className={cn(
							"rounded-md bg-muted",
							animationClasses[animation],
							className,
						)}
						style={{
							height: height || "200px",
							width: width || "100%",
						}}
						data-testid={itemTestId}
					/>
				);

			case "card":
				return (
					<div
						key={key}
						className={cn(
							"space-y-3 p-4 border border-border rounded-lg bg-card",
							className,
						)}
						data-testid={itemTestId}
					>
						<div className="flex items-center space-x-3">
							<Skeleton
								className={cn(
									"rounded-full bg-muted",
									animationClasses[animation],
								)}
								style={{ height: "40px", width: "40px" }}
							/>
							<div className="space-y-2 flex-1">
								<Skeleton
									className={cn("h-4 bg-muted", animationClasses[animation])}
									style={{ width: "60%" }}
								/>
								<Skeleton
									className={cn("h-3 bg-muted", animationClasses[animation])}
									style={{ width: "40%" }}
								/>
							</div>
						</div>
						<Skeleton
							className={cn("h-4 bg-muted", animationClasses[animation])}
							style={{ width: "100%" }}
						/>
						<Skeleton
							className={cn("h-4 bg-muted", animationClasses[animation])}
							style={{ width: "80%" }}
						/>
						<Skeleton
							className={cn("h-20 bg-muted", animationClasses[animation])}
							style={{ width: "100%" }}
						/>
					</div>
				);

			case "table":
				return (
					<div
						key={key}
						className={cn("space-y-2", className)}
						data-testid={itemTestId}
					>
						{/* Table header */}
						<div className="flex space-x-4">
							<Skeleton
								className={cn("h-4 bg-muted", animationClasses[animation])}
								style={{ width: "20%" }}
							/>
							<Skeleton
								className={cn("h-4 bg-muted", animationClasses[animation])}
								style={{ width: "30%" }}
							/>
							<Skeleton
								className={cn("h-4 bg-muted", animationClasses[animation])}
								style={{ width: "25%" }}
							/>
							<Skeleton
								className={cn("h-4 bg-muted", animationClasses[animation])}
								style={{ width: "25%" }}
							/>
						</div>
						{/* Table rows */}
						{Array.from({ length: 5 }, (_, i) => `skeleton-row-${i}`).map(
							(key) => (
								<div key={key} className="flex space-x-4">
									<Skeleton
										className={cn("h-3 bg-muted", animationClasses[animation])}
										style={{ width: "20%" }}
									/>
									<Skeleton
										className={cn("h-3 bg-muted", animationClasses[animation])}
										style={{ width: "30%" }}
									/>
									<Skeleton
										className={cn("h-3 bg-muted", animationClasses[animation])}
										style={{ width: "25%" }}
									/>
									<Skeleton
										className={cn("h-3 bg-muted", animationClasses[animation])}
										style={{ width: "25%" }}
									/>
								</div>
							),
						)}
					</div>
				);

			case "list":
				return (
					<div
						key={key}
						className={cn("space-y-3", className)}
						data-testid={itemTestId}
					>
						{Array.from({ length: 3 }, (_, i) => `skeleton-list-item-${i}`).map(
							(key) => (
								<div key={key} className="flex items-center space-x-3">
									<Skeleton
										className={cn(
											"rounded-full bg-muted",
											animationClasses[animation],
										)}
										style={{ height: "32px", width: "32px" }}
									/>
									<div className="space-y-2 flex-1">
										<Skeleton
											className={cn(
												"h-3 bg-muted",
												animationClasses[animation],
											)}
											style={{ width: "70%" }}
										/>
										<Skeleton
											className={cn(
												"h-2 bg-muted",
												animationClasses[animation],
											)}
											style={{ width: "50%" }}
										/>
									</div>
								</div>
							),
						)}
					</div>
				);
			default:
				return (
					<Skeleton
						key={key}
						className={cn(
							"h-4 bg-muted",
							animationClasses[animation],
							className,
						)}
						style={{
							height: height || "16px",
							width: width || "100%",
						}}
						data-testid={itemTestId}
					/>
				);
		}
	};

	if (count === 1) {
		return renderSkeleton(0);
	}

	return (
		<div className="space-y-3" data-testid={testId}>
			{Array.from({ length: count }).map((_, index) => renderSkeleton(index))}
		</div>
	);
}

export default SkeletonLoader;
