/**
 * ARIA Live Region Component Tests
 * Part of Phase 4: Accessibility & Performance Components
 */

import { act, fireEvent, render, screen } from "@testing-library/react";
import {
	AriaLiveRegion,
	FormValidationAnnouncer,
	LiveRegionProvider,
	StatusAnnouncer,
	useAriaLive,
	useLiveRegion,
} from "@/components/ui/aria-live-region";
import { Button } from "@/components/ui/button";
import { testLogger } from "../../test-utils";

describe("AriaLiveRegion Component", () => {
	beforeEach(() => {
		testLogger.info("Starting AriaLiveRegion test");
		vi.clearAllTimers();
		vi.useFakeTimers();
	});

	afterEach(() => {
		testLogger.info("Completed AriaLiveRegion test");
		vi.runOnlyPendingTimers();
		vi.useRealTimers();
	});

	it("renders with correct attributes", () => {
		testLogger.debug("Testing AriaLiveRegion attributes");

		render(
			<AriaLiveRegion
				message="Test message"
				politeness="assertive"
				id="test-region"
			/>,
		);

		const region = screen.getByText("Test message");
		expect(region).toHaveAttribute("aria-live", "assertive");
		expect(region).toHaveAttribute("aria-atomic", "true");
		expect(region).toHaveAttribute("id", "test-region");
		expect(region).toHaveClass("sr-only");
	});

	it("displays message correctly", () => {
		testLogger.debug("Testing message display");

		render(<AriaLiveRegion message="Hello world" />);

		expect(screen.getByText("Hello world")).toBeInTheDocument();
	});

	it("clears message after delay", async () => {
		testLogger.debug("Testing message clearing");

		const { rerender } = render(
			<AriaLiveRegion message="Test message" clearDelay={1000} />,
		);

		expect(screen.getByText("Test message")).toBeInTheDocument();

		// Fast-forward time using fake timers - use runAllTimers to ensure all pending timers execute
		act(() => {
			vi.runAllTimers();
		});

		// Message should be cleared immediately after all timers run
		expect(screen.queryByText("Test message")).not.toBeInTheDocument();
	});

	it("updates message when prop changes", () => {
		testLogger.debug("Testing message updates");

		const { rerender } = render(<AriaLiveRegion message="First message" />);

		expect(screen.getByText("First message")).toBeInTheDocument();

		rerender(<AriaLiveRegion message="Second message" />);

		expect(screen.getByText("Second message")).toBeInTheDocument();
		expect(screen.queryByText("First message")).not.toBeInTheDocument();
	});

	it("handles different politeness levels", () => {
		testLogger.debug("Testing politeness levels");

		const { rerender } = render(
			<AriaLiveRegion message="Test" politeness="polite" />,
		);

		let region = screen.getByText("Test");
		expect(region).toHaveAttribute("aria-live", "polite");

		rerender(<AriaLiveRegion message="Test" politeness="assertive" />);

		region = screen.getByText("Test");
		expect(region).toHaveAttribute("aria-live", "assertive");

		rerender(<AriaLiveRegion message="Test" politeness="off" />);

		region = screen.getByText("Test");
		expect(region).toHaveAttribute("aria-live", "off");
	});

	it("accepts custom className", () => {
		testLogger.debug("Testing custom className");

		render(<AriaLiveRegion message="Test" className="custom-class" />);

		const region = screen.getByText("Test");
		expect(region).toHaveClass("custom-class");
	});

	it("disables auto-clear when clearDelay is 0", () => {
		testLogger.debug("Testing disabled auto-clear");

		render(<AriaLiveRegion message="Persistent message" clearDelay={0} />);

		expect(screen.getByText("Persistent message")).toBeInTheDocument();

		// Fast-forward time
		vi.advanceTimersByTime(10000);

		// Message should still be there
		expect(screen.getByText("Persistent message")).toBeInTheDocument();
	});
});

describe("useAriaLive Hook", () => {
	const TestComponent = ({
		defaultPoliteness,
	}: {
		defaultPoliteness?: any;
	}) => {
		const {
			message,
			politeness,
			announce,
			announcePolite,
			announceAssertive,
			clear,
		} = useAriaLive(defaultPoliteness);

		return (
			<div>
				<div data-testid="message">{message}</div>
				<div data-testid="politeness">{politeness}</div>
				<Button onClick={() => announce("Test message", "assertive")}>
					Announce
				</Button>
				<Button onClick={() => announcePolite("Polite message")}>
					Announce Polite
				</Button>
				<Button onClick={() => announceAssertive("Assertive message")}>
					Announce Assertive
				</Button>
				<Button onClick={clear}>Clear</Button>
			</div>
		);
	};

	it("manages announcement state correctly", () => {
		testLogger.debug("Testing useAriaLive state management");

		render(<TestComponent />);

		const message = screen.getByTestId("message");
		const politeness = screen.getByTestId("politeness");

		// Initial state
		expect(message).toHaveTextContent("");
		expect(politeness).toHaveTextContent("polite");

		// Make announcement
		fireEvent.click(screen.getByText("Announce"));
		expect(message).toHaveTextContent("Test message");
		expect(politeness).toHaveTextContent("assertive");

		// Clear message
		fireEvent.click(screen.getByText("Clear"));
		expect(message).toHaveTextContent("");
	});

	it("provides convenience methods", () => {
		testLogger.debug("Testing convenience methods");

		render(<TestComponent />);

		const message = screen.getByTestId("message");
		const politeness = screen.getByTestId("politeness");

		// Test polite announcement
		fireEvent.click(screen.getByText("Announce Polite"));
		expect(message).toHaveTextContent("Polite message");
		expect(politeness).toHaveTextContent("polite");

		// Test assertive announcement
		fireEvent.click(screen.getByText("Announce Assertive"));
		expect(message).toHaveTextContent("Assertive message");
		expect(politeness).toHaveTextContent("assertive");
	});

	it("respects default politeness", () => {
		testLogger.debug("Testing default politeness");

		render(<TestComponent defaultPoliteness="assertive" />);

		const politeness = screen.getByTestId("politeness");
		expect(politeness).toHaveTextContent("assertive");
	});
});

describe("StatusAnnouncer Component", () => {
	it("formats status messages correctly", () => {
		testLogger.debug("Testing status message formatting");

		const { rerender } = render(
			<StatusAnnouncer status="loading" message="Please wait" />,
		);

		expect(screen.getByText("Loading: Please wait")).toBeInTheDocument();

		rerender(
			<StatusAnnouncer status="success" message="Operation completed" />,
		);
		expect(
			screen.getByText("Success: Operation completed"),
		).toBeInTheDocument();

		rerender(<StatusAnnouncer status="error" message="Something went wrong" />);
		expect(screen.getByText("Error: Something went wrong")).toBeInTheDocument();

		rerender(
			<StatusAnnouncer status="info" message="Additional information" />,
		);
		expect(
			screen.getByText("Info: Additional information"),
		).toBeInTheDocument();
	});

	it("uses correct politeness for status types", () => {
		testLogger.debug("Testing status politeness");

		const { rerender } = render(
			<StatusAnnouncer status="error" message="Error occurred" />,
		);

		let region = screen.getByText("Error: Error occurred");
		expect(region).toHaveAttribute("aria-live", "assertive");

		rerender(<StatusAnnouncer status="success" message="Success" />);

		region = screen.getByText("Success: Success");
		expect(region).toHaveAttribute("aria-live", "polite");
	});

	it("handles message without status", () => {
		testLogger.debug("Testing message without status");

		render(<StatusAnnouncer message="Plain message" />);

		expect(screen.getByText("Plain message")).toBeInTheDocument();
	});
});

describe("FormValidationAnnouncer Component", () => {
	it("announces single error correctly", () => {
		testLogger.debug("Testing single error announcement");

		render(
			<FormValidationAnnouncer
				errors={["This field is required"]}
				fieldName="email"
			/>,
		);

		expect(
			screen.getByText("email field: This field is required"),
		).toBeInTheDocument();
	});

	it("announces multiple errors correctly", () => {
		testLogger.debug("Testing multiple errors announcement");

		render(
			<FormValidationAnnouncer
				errors={["Field is required", "Invalid format"]}
				fieldName="password"
			/>,
		);

		expect(
			screen.getByText(
				"password field: 2 errors: Field is required, Invalid format",
			),
		).toBeInTheDocument();
	});

	it("handles no field name", () => {
		testLogger.debug("Testing without field name");

		render(<FormValidationAnnouncer errors={["Validation error"]} />);

		expect(
			screen.getByText("Validation error: Validation error"),
		).toBeInTheDocument();
	});

	it("handles empty errors array", () => {
		testLogger.debug("Testing empty errors");

		render(<FormValidationAnnouncer errors={[]} fieldName="test" />);

		// Should render but not have any error messages
		const element = document.getElementById("test-validation-announcer");
		expect(element).toBeInTheDocument();
		expect(element).toHaveTextContent("");
	});

	it("uses assertive politeness", () => {
		testLogger.debug("Testing assertive politeness");

		render(<FormValidationAnnouncer errors={["Error message"]} />);

		const region = screen.getByText("Validation error: Error message");
		expect(region).toHaveAttribute("aria-live", "assertive");
	});
});

describe("LiveRegionProvider and useLiveRegion", () => {
	const TestComponent = () => {
		const { announce, announceSuccess, announceError } = useLiveRegion();

		return (
			<div>
				<Button onClick={() => announce("Test message")}>Announce</Button>
				<Button onClick={() => announceSuccess("Success message")}>
					Success
				</Button>
				<Button onClick={() => announceError("Error message")}>Error</Button>
			</div>
		);
	};

	it("provides global announcement functionality", () => {
		testLogger.debug("Testing global announcements");

		render(
			<LiveRegionProvider>
				<TestComponent />
			</LiveRegionProvider>,
		);

		// Should render global live region
		expect(document.getElementById("global-live-region")).toBeInTheDocument();

		// Test announcements
		fireEvent.click(screen.getByText("Announce"));
		fireEvent.click(screen.getByText("Success"));
		fireEvent.click(screen.getByText("Error"));

		// Should not throw errors
		expect(screen.getByText("Announce")).toBeInTheDocument();
	});

	it("throws error when used outside provider", () => {
		testLogger.debug("Testing hook outside provider");

		const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

		expect(() => {
			render(<TestComponent />);
		}).toThrow("useLiveRegion must be used within a LiveRegionProvider");

		consoleSpy.mockRestore();
	});
});
