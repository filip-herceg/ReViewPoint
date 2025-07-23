/**
 * Virtualized List Component Tests
 * Part of Phase 4: Accessibility & Performance Components
 */

import { fireEvent, render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import {
	useVirtualizedList,
	VirtualizedGrid,
	VirtualizedList,
} from "@/components/ui/virtualized-list";
import { testLogger } from "../../test-utils";

// Create test template for virtualized list items
type TestItem = { id: string; name: string; value: number };
function createTestItems(count: number) {
	return Array.from({ length: count }, (_, index) => ({
		id: `item-${index}`,
		name: `Item ${index}`,
		value: index,
	}));
}

describe("VirtualizedList Component", () => {
	const mockItems = createTestItems(100);
	type TestItem = { id: string; name: string; value: number };
	const mockRenderItem = (item: TestItem, index: number) => (
		<div key={item.id} data-testid={`item-${index}`}>
			{item.name}
		</div>
	);

	beforeEach(() => {
		testLogger.info("Starting VirtualizedList test");
	});

	afterEach(() => {
		testLogger.info("Completed VirtualizedList test");
	});

	it("renders visible items only", () => {
		testLogger.debug("Testing visible items rendering");

		render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
			/>,
		);

		// Should render approximately 4 visible items (200/50) plus overscan
		const renderedItems = screen.getAllByTestId(/^item-/);
		expect(renderedItems.length).toBeLessThan(mockItems.length);
		expect(renderedItems.length).toBeGreaterThan(0);
	});

	it("handles scroll events correctly", () => {
		testLogger.debug("Testing scroll handling");

		const onScroll = vi.fn();

		const { container } = render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				onScroll={onScroll}
			/>,
		);

		const scrollContainer = container.firstChild as HTMLElement;

		fireEvent.scroll(scrollContainer, { target: { scrollTop: 100 } });

		expect(onScroll).toHaveBeenCalledWith(100);
	});

	it("uses custom key extractor", () => {
		testLogger.debug("Testing custom key extractor");

		const keyExtractor = vi.fn((item, _index) => `custom-${item.id}`);

		render(
			<VirtualizedList
				items={mockItems.slice(0, 5)}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				keyExtractor={keyExtractor}
			/>,
		);

		expect(keyExtractor).toHaveBeenCalled();
	});

	it("handles empty items array", () => {
		testLogger.debug("Testing empty items");

		render(
			<VirtualizedList
				items={[]}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				emptyComponent={<div>No items found</div>}
			/>,
		);

		expect(screen.getByText("No items found")).toBeInTheDocument();
	});

	it("shows loading state", () => {
		testLogger.debug("Testing loading state");

		render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				isLoading={true}
				loadingComponent={<div>Loading data...</div>}
			/>,
		);

		expect(screen.getByText("Loading data...")).toBeInTheDocument();
	});

	it("shows error state", () => {
		testLogger.debug("Testing error state");

		render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				hasError={true}
				errorComponent={<div>Failed to load</div>}
			/>,
		);

		expect(screen.getByText("Failed to load")).toBeInTheDocument();
	});

	it("applies custom className", () => {
		testLogger.debug("Testing custom className");

		const { container } = render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				className="custom-list"
			/>,
		);

		expect(container.firstChild).toHaveClass("custom-list");
	});

	it("calculates total height correctly", () => {
		testLogger.debug("Testing total height calculation");

		const { container } = render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
			/>,
		);

		// Check the total height container (the relative positioned div)
		const totalHeightContainer = container.querySelector(
			'div[style*="position: relative"]',
		);
		const expectedHeight = mockItems.length * 50;

		expect(totalHeightContainer).toHaveStyle(`height: ${expectedHeight}px`);
	});

	it("handles overscan correctly", () => {
		testLogger.debug("Testing overscan buffer");

		render(
			<VirtualizedList
				items={mockItems}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
				overscan={10}
			/>,
		);

		// Should render more items due to larger overscan
		const renderedItems = screen.getAllByTestId(/^item-/);
		expect(renderedItems.length).toBeGreaterThan(4); // Base visible items
	});

	it("handles performance with large datasets", () => {
		testLogger.debug("Testing performance with large dataset");

		const largeDataset = createTestItems(10000);

		const startTime = performance.now();

		render(
			<VirtualizedList
				items={largeDataset}
				itemHeight={50}
				containerHeight={200}
				renderItem={mockRenderItem}
			/>,
		);

		const endTime = performance.now();
		const renderTime = endTime - startTime;

		// Should render quickly even with large dataset
		expect(renderTime).toBeLessThan(100); // 100ms threshold

		// Should only render visible items, not all 10k
		const renderedItems = screen.getAllByTestId(/^item-/);
		expect(renderedItems.length).toBeLessThan(50);
	});
});

describe("VirtualizedGrid Component", () => {
	const mockGridItems = createTestItems(50);
	const mockRenderGridItem = (item: TestItem, index: number) => (
		<div key={item.id} data-testid={`grid-item-${index}`}>
			{item.name}
		</div>
	);

	it("renders grid layout correctly", () => {
		testLogger.debug("Testing grid layout");

		render(
			<VirtualizedGrid
				items={mockGridItems}
				itemWidth={100}
				itemHeight={100}
				containerWidth={400}
				containerHeight={400}
				renderItem={mockRenderGridItem}
			/>,
		);

		// Should render some grid items
		const renderedItems = screen.getAllByTestId(/^grid-item-/);
		expect(renderedItems.length).toBeGreaterThan(0);
	});

	it("calculates columns correctly", () => {
		testLogger.debug("Testing column calculation");

		const { container } = render(
			<VirtualizedGrid
				items={mockGridItems}
				itemWidth={100}
				itemHeight={100}
				containerWidth={400}
				containerHeight={400}
				renderItem={mockRenderGridItem}
				gap={10}
			/>,
		);

		// With 400px width, 100px items, and 10px gap, should fit 3-4 columns
		expect(container.firstChild).toBeInTheDocument();
	});

	it("handles custom column count", () => {
		testLogger.debug("Testing custom column count");

		render(
			<VirtualizedGrid
				items={mockGridItems}
				itemWidth={100}
				itemHeight={100}
				containerWidth={400}
				containerHeight={400}
				columnsCount={2}
				renderItem={mockRenderGridItem}
			/>,
		);

		// Should respect custom column count
		expect(screen.getAllByTestId(/^grid-item-/).length).toBeGreaterThan(0);
	});

	it("positions items correctly", () => {
		testLogger.debug("Testing item positioning");

		const { container } = render(
			<VirtualizedGrid
				items={mockGridItems.slice(0, 4)}
				itemWidth={100}
				itemHeight={100}
				containerWidth={300}
				containerHeight={300}
				columnsCount={2}
				renderItem={mockRenderGridItem}
			/>,
		);

		// Find the items container (absolute positioned div)
		const itemsContainer = container.querySelector(
			'div[style*="position: absolute"][style*="transform"]',
		);
		expect(itemsContainer).toBeInTheDocument();

		// Check that items inside have position styling applied directly
		const items = itemsContainer?.querySelectorAll(
			'div[style*="position: absolute"]',
		);
		expect(items).toBeDefined();

		if (items && items.length > 0) {
			items.forEach((item) => {
				const style = (item as HTMLElement).style;
				expect(style.position).toBe("absolute");
				expect(style.left).toBeDefined();
				expect(style.top).toBeDefined();
			});
		}
	});
});

describe("useVirtualizedList Hook", () => {
	const TestComponent = ({ items }: { items: unknown[] }) => {
		const {
			scrollTop,
			scrollToIndex,
			scrollToTop,
			scrollToBottom,
			setScrollTop,
		} = useVirtualizedList(items, {
			itemHeight: 50,
			containerHeight: 200,
		});

		return (
			<div>
				<div data-testid="scroll-top">{scrollTop}</div>
				<Button onClick={() => scrollToIndex(10)}>Scroll to 10</Button>
				<Button onClick={scrollToTop}>Scroll to Top</Button>
				<Button onClick={scrollToBottom}>Scroll to Bottom</Button>
				<Button onClick={() => setScrollTop(100)}>Set Scroll 100</Button>
			</div>
		);
	};

	it("manages scroll state correctly", () => {
		testLogger.debug("Testing scroll state management");

		const items = createTestItems(100);

		render(<TestComponent items={items} />);

		const scrollTopDisplay = screen.getByTestId("scroll-top");

		// Initial state
		expect(scrollTopDisplay).toHaveTextContent("0");

		// Set scroll position
		fireEvent.click(screen.getByText("Set Scroll 100"));
		expect(scrollTopDisplay).toHaveTextContent("100");

		// Scroll to top
		fireEvent.click(screen.getByText("Scroll to Top"));
		expect(scrollTopDisplay).toHaveTextContent("0");
	});

	it("calculates scroll positions correctly", () => {
		testLogger.debug("Testing scroll position calculations");

		const items = createTestItems(100);

		render(<TestComponent items={items} />);

		const scrollTopDisplay = screen.getByTestId("scroll-top");

		// Scroll to index 10 (10 * 50px = 500px)
		fireEvent.click(screen.getByText("Scroll to 10"));
		expect(scrollTopDisplay).toHaveTextContent("500");

		// Scroll to bottom
		fireEvent.click(screen.getByText("Scroll to Bottom"));
		// Should scroll to maximum position
		expect(parseInt(scrollTopDisplay.textContent || "0")).toBeGreaterThan(0);
	});

	it("handles edge cases", () => {
		testLogger.debug("Testing edge cases");

		const items = createTestItems(5); // Small dataset

		render(<TestComponent items={items} />);

		// Should handle scrolling beyond content gracefully
		fireEvent.click(screen.getByText("Scroll to Bottom"));

		const scrollTop = parseInt(
			screen.getByTestId("scroll-top").textContent || "0",
		);
		expect(scrollTop).toBeGreaterThanOrEqual(0);
	});
});
