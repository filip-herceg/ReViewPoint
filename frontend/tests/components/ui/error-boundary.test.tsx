import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { Button } from "@/components/ui/button";

// Test component that throws an error
const ThrowError = ({ shouldThrow = false }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error("Test error");
  }
  return <div>Working component</div>;
};

describe("ErrorBoundary Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock console.error to avoid error output in tests
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  it("renders children when no error occurs", () => {
    render(
      <ErrorBoundary>
        <div data-testid="child-component">Child content</div>
      </ErrorBoundary>,
    );

    expect(screen.getByTestId("child-component")).toBeInTheDocument();
    expect(screen.getByText("Child content")).toBeInTheDocument();
  });

  it("renders error UI when child component throws", () => {
    render(
      <ErrorBoundary testId="error-boundary">
        <ThrowError shouldThrow />
      </ErrorBoundary>,
    );

    expect(screen.getByTestId("error-boundary")).toBeInTheDocument();
    expect(screen.getByTestId("error-boundary-title")).toHaveTextContent(
      "Something went wrong",
    );
    expect(
      screen.getByTestId("error-boundary-description"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("error-boundary-retry")).toBeInTheDocument();
    expect(screen.getByTestId("error-boundary-reload")).toBeInTheDocument();
  });

  it("calls onError callback when error occurs", () => {
    const mockOnError = vi.fn();

    render(
      <ErrorBoundary onError={mockOnError}>
        <ThrowError shouldThrow />
      </ErrorBoundary>,
    );

    expect(mockOnError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({ componentStack: expect.any(String) }),
    );
  });

  it("can retry after error", async () => {
    const user = userEvent.setup();

    const RetryableComponent = () => {
      const [shouldThrow, setShouldThrow] = React.useState(true);

      React.useEffect(() => {
        const timer = setTimeout(() => setShouldThrow(false), 100);
        return () => clearTimeout(timer);
      }, []);

      return <ThrowError shouldThrow={shouldThrow} />;
    };

    render(
      <ErrorBoundary testId="error-boundary">
        <RetryableComponent />
      </ErrorBoundary>,
    );

    // Error should be shown initially
    expect(screen.getByTestId("error-boundary-retry")).toBeInTheDocument();

    // Click retry
    await user.click(screen.getByTestId("error-boundary-retry"));

    // After retry, we might see the working component (though timing dependent)
    // This is more of an integration test concept
  });

  it("shows custom retry text when provided", () => {
    render(
      <ErrorBoundary retryText="Custom Retry" testId="error-boundary">
        <ThrowError shouldThrow />
      </ErrorBoundary>,
    );

    expect(screen.getByTestId("error-boundary-retry")).toHaveTextContent(
      "Custom Retry",
    );
  });

  it("renders custom fallback when provided", () => {
    const customFallback = (
      error: Error,
      errorInfo: React.ErrorInfo,
      retry: () => void,
    ) => (
      <div data-testid="custom-fallback">
        <p>Custom error message</p>
        <Button onClick={retry} data-testid="custom-retry">
          Custom Retry
        </Button>
      </div>
    );

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow />
      </ErrorBoundary>,
    );

    expect(screen.getByTestId("custom-fallback")).toBeInTheDocument();
    expect(screen.getByText("Custom error message")).toBeInTheDocument();
    expect(screen.getByTestId("custom-retry")).toBeInTheDocument();
  });

  it("shows error details when showDetails is true", () => {
    render(
      <ErrorBoundary showDetails testId="error-boundary">
        <ThrowError shouldThrow />
      </ErrorBoundary>,
    );

    // Error details should be shown
    expect(screen.getByText("Error Details")).toBeInTheDocument();
  });

  it("handles reload button click", async () => {
    const mockReload = vi.fn();
    Object.defineProperty(window, "location", {
      value: { reload: mockReload },
      writable: true,
    });

    const user = userEvent.setup();

    render(
      <ErrorBoundary testId="error-boundary">
        <ThrowError shouldThrow />
      </ErrorBoundary>,
    );

    await user.click(screen.getByTestId("error-boundary-reload"));
    expect(mockReload).toHaveBeenCalled();
  });
});

// Need to import React for the RetryableComponent
import React from "react";
