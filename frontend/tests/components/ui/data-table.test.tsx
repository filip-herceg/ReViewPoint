import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  DataTable,
  type DataTableColumn,
  type DataTableProps,
} from "@/components/ui/data-table";

// Test data
interface TestUser {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
  status: "active" | "inactive";
  lastLogin: string;
}

const mockUsers: TestUser[] = [
  {
    id: 1,
    name: "John Doe",
    email: "john@example.com",
    role: "admin",
    status: "active",
    lastLogin: "2024-01-15",
  },
  {
    id: 2,
    name: "Jane Smith",
    email: "jane@example.com",
    role: "user",
    status: "active",
    lastLogin: "2024-01-14",
  },
  {
    id: 3,
    name: "Bob Johnson",
    email: "bob@example.com",
    role: "user",
    status: "inactive",
    lastLogin: "2024-01-10",
  },
];

const defaultColumns: DataTableColumn<TestUser>[] = [
  { key: "name", title: "Name", sortable: true },
  { key: "email", title: "Email", sortable: true },
  { key: "role", title: "Role", filterable: true },
  {
    key: "status",
    title: "Status",
    render: (value) => (
      <span className={value === "active" ? "text-green-600" : "text-red-600"}>
        {value}
      </span>
    ),
  },
];

const defaultProps: DataTableProps<TestUser> = {
  data: mockUsers,
  columns: defaultColumns,
  testId: "test-table",
};

describe("DataTable Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders table with data correctly", () => {
    render(<DataTable {...defaultProps} />);

    // Check headers
    expect(screen.getByTestId("test-table-header-name")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-header-email")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-header-role")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-header-status")).toBeInTheDocument();

    // Check data rows
    expect(screen.getByTestId("test-table-row-0")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-row-1")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-row-2")).toBeInTheDocument();

    // Check cell content
    expect(screen.getByTestId("test-table-cell-0-name")).toHaveTextContent(
      "John Doe",
    );
    expect(screen.getByTestId("test-table-cell-1-email")).toHaveTextContent(
      "jane@example.com",
    );
  });

  it("handles sorting correctly", async () => {
    const mockOnSort = vi.fn();
    const user = userEvent.setup();

    const { rerender } = render(
      <DataTable
        {...defaultProps}
        sorting={{
          config: null,
          onSort: mockOnSort,
        }}
      />,
    );

    // Click on sortable header
    await user.click(screen.getByTestId("test-table-header-name"));

    expect(mockOnSort).toHaveBeenCalledWith({ key: "name", direction: "asc" });

    // Simulate second click (toggle to desc) using rerender
    rerender(
      <DataTable
        {...defaultProps}
        sorting={{
          config: { key: "name", direction: "asc" },
          onSort: mockOnSort,
        }}
      />,
    );

    await user.click(screen.getByTestId("test-table-header-name"));
    expect(mockOnSort).toHaveBeenCalledWith({ key: "name", direction: "desc" });
  });

  it("handles filtering correctly", async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    // Use state to simulate controlled input
    let filterValue = "";
    const updateFilterValue = (newValue: string) => {
      filterValue = newValue;
      mockOnFilterChange(newValue);
    };

    const { rerender } = render(
      <DataTable
        {...defaultProps}
        filtering={{
          value: filterValue,
          onChange: updateFilterValue,
          placeholder: "Search users...",
        }}
      />,
    );

    const filterInput = screen.getByTestId("test-table-filter");
    expect(filterInput).toBeInTheDocument();
    expect(filterInput).toHaveAttribute("placeholder", "Search users...");

    // Type one character at a time and rerender to update the controlled value
    await user.type(filterInput, "j");
    filterValue = "j";
    rerender(
      <DataTable
        {...defaultProps}
        filtering={{
          value: filterValue,
          onChange: updateFilterValue,
          placeholder: "Search users...",
        }}
      />,
    );

    // Check the final state
    expect(filterInput).toHaveValue("j");
    expect(mockOnFilterChange).toHaveBeenCalledWith("j");
  });

  it("handles selection correctly", async () => {
    const mockOnSelectionChange = vi.fn();
    const selectedRows = new Set<number>();
    const user = userEvent.setup();

    render(
      <DataTable
        {...defaultProps}
        selection={{
          selectedRows,
          onSelectionChange: mockOnSelectionChange,
        }}
      />,
    );

    // Check select all checkbox exists
    const selectAllCheckbox = screen.getByTestId("test-table-select-all");
    expect(selectAllCheckbox).toBeInTheDocument();

    // Select individual row
    const rowCheckbox = screen.getByTestId("test-table-select-0");
    await user.click(rowCheckbox);

    expect(mockOnSelectionChange).toHaveBeenCalledWith(new Set([0]));
  });

  it("handles pagination correctly", async () => {
    const mockOnPageChange = vi.fn();
    const mockOnPageSizeChange = vi.fn();
    const user = userEvent.setup();

    render(
      <DataTable
        {...defaultProps}
        pagination={{
          page: 1,
          pageSize: 10,
          total: 25,
          onPageChange: mockOnPageChange,
          onPageSizeChange: mockOnPageSizeChange,
        }}
      />,
    );

    // Check pagination controls
    expect(screen.getByTestId("test-table-pagination")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-page-size")).toBeInTheDocument();
    expect(screen.getByTestId("test-table-next-page")).toBeInTheDocument();

    // Test page navigation
    await user.click(screen.getByTestId("test-table-next-page"));
    expect(mockOnPageChange).toHaveBeenCalledWith(2);
  });

  it("shows loading skeleton", () => {
    render(<DataTable {...defaultProps} loading={true} />);

    expect(screen.getByTestId("test-table-loading")).toBeInTheDocument();
    expect(screen.queryByTestId("test-table-table")).not.toBeInTheDocument();
  });

  it("shows error state", () => {
    const errorMessage = "Failed to load data";
    render(<DataTable {...defaultProps} error={errorMessage} />);

    expect(screen.getByTestId("test-table-error")).toBeInTheDocument();
    expect(screen.getByText("Error loading data")).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("has proper ARIA attributes", () => {
    render(<DataTable {...defaultProps} />);

    const table = screen.getByTestId("test-table-table");
    expect(table).toBeInTheDocument();
    expect(table.tagName).toBe("TABLE");

    // Check headers have proper structure
    const headers = screen.getAllByRole("columnheader");
    expect(headers).toHaveLength(4);
  });

  it("shows empty state when no data", () => {
    render(
      <DataTable {...defaultProps} data={[]} emptyMessage="No users found" />,
    );

    expect(screen.getByTestId("test-table-empty")).toBeInTheDocument();
    expect(screen.getByText("No users found")).toBeInTheDocument();
  });

  it("handles large datasets efficiently", () => {
    const largeDataset: TestUser[] = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      name: `User ${i}`,
      email: `user${i}@example.com`,
      role: i % 2 === 0 ? "admin" : "user",
      status: i % 3 === 0 ? "inactive" : "active",
      lastLogin: "2024-01-15",
    }));

    const startTime = performance.now();
    render(<DataTable {...defaultProps} data={largeDataset} />);
    const endTime = performance.now();

    // Should render within reasonable time (less than 500ms for large datasets)
    expect(endTime - startTime).toBeLessThan(500);

    // Should only render visible rows efficiently
    expect(screen.getByTestId("test-table-table")).toBeInTheDocument();
  });

  it("handles invalid column configuration", () => {
    const invalidColumns: DataTableColumn<TestUser>[] = [
      { key: "nonExistentField" as keyof TestUser, title: "Invalid" },
    ];

    render(<DataTable {...defaultProps} columns={invalidColumns} />);

    // Should not crash and should render table structure
    expect(screen.getByTestId("test-table-table")).toBeInTheDocument();
  });

  it("clears filter correctly", async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <DataTable
        {...defaultProps}
        filtering={{
          value: "john",
          onChange: mockOnFilterChange,
        }}
      />,
    );

    const clearButton = screen.getByTestId("test-table-clear-filter");
    await user.click(clearButton);

    expect(mockOnFilterChange).toHaveBeenCalledWith("");
  });

  it("works with custom renderers", () => {
    const customColumns: DataTableColumn<TestUser>[] = [
      {
        key: "status",
        title: "Status",
        render: (value, row) => (
          <div
            data-testid={`status-${row.id}`}
            className={value === "active" ? "text-green-600" : "text-red-600"}
          >
            {value.toUpperCase()}
          </div>
        ),
      },
    ];

    render(<DataTable {...defaultProps} columns={customColumns} />);

    expect(screen.getByTestId("status-1")).toHaveTextContent("ACTIVE");
    expect(screen.getByTestId("status-3")).toHaveTextContent("INACTIVE");
  });

  it("adapts to different screen sizes", () => {
    // Test mobile view
    Object.defineProperty(window, "innerWidth", { value: 375 });
    const { rerender } = render(<DataTable {...defaultProps} />);

    const table = screen.getByTestId("test-table-table");
    expect(table).toBeInTheDocument();

    // Test desktop view
    Object.defineProperty(window, "innerWidth", { value: 1024 });
    rerender(<DataTable {...defaultProps} />);

    expect(screen.getByTestId("test-table-table")).toBeInTheDocument();
  });
});
