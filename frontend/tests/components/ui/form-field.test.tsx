import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FormField } from "@/components/ui/form-field";

describe("FormField Component", () => {
  const defaultProps = {
    name: "test-field",
    label: "Test Field",
    testId: "test-form-field",
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders basic text input correctly", () => {
    render(<FormField {...defaultProps} />);

    expect(screen.getByTestId("test-form-field")).toBeInTheDocument();
    expect(screen.getByTestId("test-form-field-label")).toHaveTextContent(
      "Test Field",
    );
    expect(screen.getByTestId("test-form-field-input")).toBeInTheDocument();
    expect(screen.getByTestId("test-form-field-input")).toHaveAttribute(
      "type",
      "text",
    );
  });

  it("shows required indicator when required is true", () => {
    render(<FormField {...defaultProps} required />);

    const label = screen.getByTestId("test-form-field-label");
    expect(label).toHaveClass("after:content-['*']");
  });

  it("displays error message when error is provided", () => {
    const errorMessage = "This field is required";
    render(<FormField {...defaultProps} error={errorMessage} />);

    expect(screen.getByTestId("test-form-field-error")).toHaveTextContent(
      errorMessage,
    );
    expect(screen.getByTestId("test-form-field-input")).toHaveAttribute(
      "aria-invalid",
      "true",
    );
  });

  it("handles text input changes", async () => {
    const mockOnChange = vi.fn();
    const user = userEvent.setup();

    // Create a controlled component that updates its value
    const ControlledFormField = () => {
      const [value, setValue] = React.useState("");

      return (
        <FormField
          {...defaultProps}
          value={value}
          onChange={(newValue) => {
            setValue(newValue);
            mockOnChange(newValue);
          }}
        />
      );
    };

    render(<ControlledFormField />);

    const input = screen.getByTestId("test-form-field-input");

    // Type the text and check that onChange is called
    await user.type(input, "test value");

    // The onChange handler should be called for each character typed
    expect(mockOnChange).toHaveBeenCalledTimes(10); // 'test value' has 10 characters

    // Check that the component is working correctly
    expect(mockOnChange).toHaveBeenCalled();
    expect(input).toHaveValue("test value");
  });

  it("renders textarea when type is textarea", () => {
    render(<FormField {...defaultProps} type="textarea" />);

    const textarea = screen.getByTestId("test-form-field-input");
    expect(textarea.tagName).toBe("TEXTAREA");
    expect(textarea).toHaveAttribute("rows", "4");
  });

  it("renders select when type is select", () => {
    const options = [
      { value: "option1", label: "Option 1" },
      { value: "option2", label: "Option 2" },
    ];

    render(
      <FormField
        {...defaultProps}
        type="select"
        options={options}
        placeholder="Select an option"
      />,
    );

    expect(screen.getByTestId("test-form-field-select")).toBeInTheDocument();
    expect(screen.getByText("Select an option")).toBeInTheDocument();
  });

  it.skip("handles select changes", async () => {
    // TODO: Fix this test - the Radix Select component has pointer capture issues in test environment
    const mockOnChange = vi.fn();
    const user = userEvent.setup();
    const options = [
      { value: "option1", label: "Option 1" },
      { value: "option2", label: "Option 2" },
    ];

    render(
      <FormField
        {...defaultProps}
        type="select"
        options={options}
        onChange={mockOnChange}
      />,
    );

    const select = screen.getByTestId("test-form-field-select");
    await user.click(select);

    const option = screen.getByTestId("test-form-field-option-option1");
    await user.click(option);

    expect(mockOnChange).toHaveBeenCalledWith("option1");
  });

  it("disables input when disabled is true", () => {
    render(<FormField {...defaultProps} disabled />);

    const input = screen.getByTestId("test-form-field-input");
    expect(input).toBeDisabled();
  });

  it("handles different input types correctly", () => {
    const { rerender } = render(<FormField {...defaultProps} type="email" />);
    expect(screen.getByTestId("test-form-field-input")).toHaveAttribute(
      "type",
      "email",
    );

    rerender(<FormField {...defaultProps} type="password" />);
    expect(screen.getByTestId("test-form-field-input")).toHaveAttribute(
      "type",
      "password",
    );

    rerender(<FormField {...defaultProps} type="number" />);
    expect(screen.getByTestId("test-form-field-input")).toHaveAttribute(
      "type",
      "number",
    );
  });

  it("handles blur events", async () => {
    const mockOnBlur = vi.fn();
    const user = userEvent.setup();

    render(<FormField {...defaultProps} onBlur={mockOnBlur} />);

    const input = screen.getByTestId("test-form-field-input");
    await user.click(input);
    await user.tab();

    expect(mockOnBlur).toHaveBeenCalled();
  });

  it("applies custom className", () => {
    render(<FormField {...defaultProps} className="custom-class" />);

    const container = screen.getByTestId("test-form-field");
    expect(container).toHaveClass("custom-class");
  });

  it("sets placeholder correctly", () => {
    const placeholder = "Enter your value";
    render(<FormField {...defaultProps} placeholder={placeholder} />);

    const input = screen.getByTestId("test-form-field-input");
    expect(input).toHaveAttribute("placeholder", placeholder);
  });

  it("sets initial value correctly", () => {
    const initialValue = "initial value";
    render(<FormField {...defaultProps} value={initialValue} />);

    const input = screen.getByTestId("test-form-field-input");
    expect(input).toHaveValue(initialValue);
  });
});
