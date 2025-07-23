/**
 * Virtualized List Component
 * High-performance list component for large datasets
 * Part of Phase 4: Accessibility & Performance Components
 */

import type React from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import logger from "@/logger";

interface VirtualizedListProps<T> {
	items: T[];
	itemHeight: number;
	containerHeight: number;
	renderItem: (item: T, index: number) => React.ReactNode;
	keyExtractor?: (item: T, index: number) => string | number;
	overscan?: number;
	className?: string;
	onScroll?: (scrollTop: number) => void;
	loadingComponent?: React.ReactNode;
	emptyComponent?: React.ReactNode;
	errorComponent?: React.ReactNode;
	isLoading?: boolean;
	hasError?: boolean;
}

/**
 * High-performance virtualized list component
 * Only renders visible items plus overscan buffer
 *
 * @example
 * ```tsx
 * <VirtualizedList
 *   items={largeDataset}
 *   itemHeight={50}
 *   containerHeight={400}
 *   renderItem={(item, index) => (
 *     <div key={item.id}>{item.name}</div>
 *   )}
 *   keyExtractor={(item) => item.id}
 * />
 * ```
 */
export function VirtualizedList<T>({
	items,
	itemHeight,
	containerHeight,
	renderItem,
	keyExtractor = (_, index) => index,
	overscan = 5,
	className,
	onScroll,
	loadingComponent,
	emptyComponent,
	errorComponent,
	isLoading = false,
	hasError = false,
}: VirtualizedListProps<T>) {
	const [scrollTop, setScrollTop] = useState(0);
	const scrollElementRef = useRef<HTMLDivElement>(null);

	// Calculate visible range
	const visibleRange = useMemo(() => {
		const visibleStart = Math.floor(scrollTop / itemHeight);
		const visibleEnd = Math.min(
			visibleStart + Math.ceil(containerHeight / itemHeight),
			items.length,
		);

		const startIndex = Math.max(0, visibleStart - overscan);
		const endIndex = Math.min(items.length, visibleEnd + overscan);

		return { startIndex, endIndex };
	}, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

	// Get visible items
	const visibleItems = useMemo(() => {
		const { startIndex, endIndex } = visibleRange;
		return items.slice(startIndex, endIndex).map((item, index) => ({
			item,
			index: startIndex + index,
			key: keyExtractor(item, startIndex + index),
		}));
	}, [items, visibleRange, keyExtractor]);

	// Handle scroll events
	const handleScroll = useCallback(
		(event: React.UIEvent<HTMLDivElement>) => {
			const newScrollTop = event.currentTarget.scrollTop;
			setScrollTop(newScrollTop);
			onScroll?.(newScrollTop);
		},
		[onScroll],
	);

	// Calculate total height and offset
	const totalHeight = items.length * itemHeight;
	const offsetY = visibleRange.startIndex * itemHeight;

	// Log performance metrics
	useEffect(() => {
		logger.debug("VirtualizedList: Render metrics", {
			totalItems: items.length,
			visibleItems: visibleItems.length,
			startIndex: visibleRange.startIndex,
			endIndex: visibleRange.endIndex,
			scrollTop,
			itemHeight,
			containerHeight,
		});
	}, [
		items.length,
		visibleItems.length,
		visibleRange,
		scrollTop,
		itemHeight,
		containerHeight,
	]);

	// Show loading state
	if (isLoading) {
		return (
			<div
				className={cn("flex items-center justify-center p-8", className)}
				style={{ height: containerHeight }}
			>
				{loadingComponent || (
					<div className="text-muted-foreground">Loading...</div>
				)}
			</div>
		);
	}

	// Show error state
	if (hasError) {
		return (
			<div
				className={cn("flex items-center justify-center p-8", className)}
				style={{ height: containerHeight }}
			>
				{errorComponent || (
					<div className="text-destructive">Error loading data</div>
				)}
			</div>
		);
	}

	// Show empty state
	if (items.length === 0) {
		return (
			<div
				className={cn("flex items-center justify-center p-8", className)}
				style={{ height: containerHeight }}
			>
				{emptyComponent || (
					<div className="text-muted-foreground">No items to display</div>
				)}
			</div>
		);
	}

	return (
		<div
			ref={scrollElementRef}
			className={cn("overflow-auto", className)}
			style={{ height: containerHeight }}
			onScroll={handleScroll}
		>
			{/* Total height container */}
			<div style={{ height: totalHeight, position: "relative" }}>
				{/* Visible items container */}
				<div
					style={{
						transform: `translateY(${offsetY}px)`,
						position: "absolute",
						top: 0,
						left: 0,
						right: 0,
					}}
				>
					{visibleItems.map(({ item, index, key }) => (
						<div
							key={key}
							style={{ height: itemHeight }}
							className="virtualized-list-item"
						>
							{renderItem(item, index)}
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

/**
 * Hook for managing virtualized list state
 */
export function useVirtualizedList<T>(
	items: T[],
	options?: {
		itemHeight?: number;
		containerHeight?: number;
		overscan?: number;
	},
) {
	const {
		itemHeight = 50,
		containerHeight = 400,
		// overscan = 5, // Currently unused but kept for future implementation
	} = options || {};

	const [scrollTop, setScrollTop] = useState(0);

	const scrollToIndex = useCallback(
		(index: number) => {
			const targetScrollTop = index * itemHeight;
			setScrollTop(targetScrollTop);
			logger.info("VirtualizedList: Scrolled to index", {
				index,
				scrollTop: targetScrollTop,
			});
		},
		[itemHeight],
	);

	const scrollToTop = useCallback(() => {
		setScrollTop(0);
		logger.info("VirtualizedList: Scrolled to top");
	}, []);

	const scrollToBottom = useCallback(() => {
		const targetScrollTop = Math.max(
			0,
			items.length * itemHeight - containerHeight,
		);
		setScrollTop(targetScrollTop);
		logger.info("VirtualizedList: Scrolled to bottom");
	}, [items.length, itemHeight, containerHeight]);

	return {
		scrollTop,
		scrollToIndex,
		scrollToTop,
		scrollToBottom,
		setScrollTop,
	};
}

/**
 * Virtualized Grid Component
 * For 2D virtualization of grid layouts
 */
interface VirtualizedGridProps<T> {
	items: T[];
	itemWidth: number;
	itemHeight: number;
	containerWidth: number;
	containerHeight: number;
	columnsCount?: number;
	renderItem: (item: T, index: number) => React.ReactNode;
	keyExtractor?: (item: T, index: number) => string | number;
	gap?: number;
	className?: string;
}

export function VirtualizedGrid<T>({
	items,
	itemWidth,
	itemHeight,
	containerWidth,
	containerHeight,
	columnsCount,
	renderItem,
	keyExtractor = (_, index) => index,
	gap = 0,
	className,
}: VirtualizedGridProps<T>) {
	const [scrollTop, setScrollTop] = useState(0);

	// Calculate columns based on container width if not provided
	const columns =
		columnsCount || Math.floor((containerWidth + gap) / (itemWidth + gap));
	const rows = Math.ceil(items.length / columns);

	// Calculate visible row range
	const visibleRowStart = Math.floor(scrollTop / (itemHeight + gap));
	const visibleRowEnd = Math.min(
		visibleRowStart + Math.ceil(containerHeight / (itemHeight + gap)) + 1,
		rows,
	);

	// Get visible items
	const visibleItems = useMemo(() => {
		const result: Array<{
			item: T;
			index: number;
			row: number;
			col: number;
			key: string | number;
		}> = [];

		for (let row = visibleRowStart; row < visibleRowEnd; row++) {
			for (let col = 0; col < columns; col++) {
				const index = row * columns + col;
				if (index >= items.length) break;

				result.push({
					item: items[index],
					index,
					row,
					col,
					key: keyExtractor(items[index], index),
				});
			}
		}

		return result;
	}, [items, visibleRowStart, visibleRowEnd, columns, keyExtractor]);

	const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
		setScrollTop(event.currentTarget.scrollTop);
	}, []);

	const totalHeight = rows * (itemHeight + gap) - gap;
	const offsetY = visibleRowStart * (itemHeight + gap);

	return (
		<div
			className={cn("overflow-auto", className)}
			style={{ height: containerHeight, width: containerWidth }}
			onScroll={handleScroll}
		>
			<div style={{ height: totalHeight, position: "relative" }}>
				<div
					style={{
						transform: `translateY(${offsetY}px)`,
						position: "absolute",
						top: 0,
						left: 0,
						right: 0,
					}}
				>
					{visibleItems.map(({ item, index, row, col, key }) => (
						<div
							key={key}
							style={{
								position: "absolute",
								left: col * (itemWidth + gap),
								top: (row - visibleRowStart) * (itemHeight + gap),
								width: itemWidth,
								height: itemHeight,
							}}
						>
							{renderItem(item, index)}
						</div>
					))}
				</div>
			</div>
		</div>
	);
}
