/**
 * DataTable Component - Reusable data table with sorting, filtering, and pagination
 * Part of Phase 2.4 UI Design System
 */

import type React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import logger from "@/logger";

// Column definition
export interface DataTableColumn<T> {
  key: keyof T | string;
  title: string;
  sortable?: boolean;
  filterable?: boolean;
  width?: string | number;
  render?: (value: unknown, row: T, index: number) => React.ReactNode;
  className?: string;
}

// Sort configuration
export interface SortConfig {
  key: string;
  direction: "asc" | "desc";
}

// DataTable props
export interface DataTableProps<T> {
  data: T[];
  columns: DataTableColumn<T>[];
  loading?: boolean;
  error?: string | null;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
    onPageSizeChange: (size: number) => void;
  };
  sorting?: {
    config: SortConfig | null;
    onSort: (config: SortConfig | null) => void;
  };
  filtering?: {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
  };
  selection?: {
    selectedRows: Set<number>;
    onSelectionChange: (selected: Set<number>) => void;
    selectable?: (row: T, index: number) => boolean;
  };
  className?: string;
  emptyMessage?: string;
  testId?: string;
}

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

/**
 * Reusable DataTable component with comprehensive features
 */
export function DataTable<T extends Record<string, unknown>>({
  data,
  columns,
  loading = false,
  error = null,
  pagination,
  sorting,
  filtering,
  selection,
  className,
  emptyMessage = "No data available",
  testId = "data-table",
}: DataTableProps<T>) {
  // Handle sort
  const handleSort = (columnKey: string) => {
    if (!sorting) return;

    try {
      const { config, onSort } = sorting;
      let newConfig: SortConfig | null = null;

      if (config?.key === columnKey) {
        // Same column: toggle direction or clear
        if (config.direction === "asc") {
          newConfig = { key: columnKey, direction: "desc" };
        } else {
          newConfig = null; // Clear sort
        }
      } else {
        // New column: start with ascending
        newConfig = { key: columnKey, direction: "asc" };
      }

      onSort(newConfig);
      logger.debug("DataTable sort changed", { columnKey, config: newConfig });
    } catch (err) {
      logger.error("Failed to handle sort", { columnKey, error: err });
    }
  };

  // Handle selection
  const handleRowSelection = (index: number, selected: boolean) => {
    if (!selection) return;

    try {
      const newSelection = new Set(selection.selectedRows);
      if (selected) {
        newSelection.add(index);
      } else {
        newSelection.delete(index);
      }
      selection.onSelectionChange(newSelection);
      logger.debug("DataTable selection changed", {
        index,
        selected,
        total: newSelection.size,
      });
    } catch (err) {
      logger.error("Failed to handle row selection", {
        index,
        selected,
        error: err,
      });
    }
  };

  // Handle select all
  const handleSelectAll = (selected: boolean) => {
    if (!selection) return;

    try {
      const newSelection = new Set<number>();
      if (selected) {
        data.forEach((row, index) => {
          if (!selection.selectable || selection.selectable(row, index)) {
            newSelection.add(index);
          }
        });
      }
      selection.onSelectionChange(newSelection);
      logger.debug("DataTable select all changed", {
        selected,
        total: newSelection.size,
      });
    } catch (err) {
      logger.error("Failed to handle select all", { selected, error: err });
    }
  };

  // Render loading skeleton
  if (loading) {
    return (
      <div
        className={cn("space-y-4", className)}
        data-testid={`${testId}-loading`}
      >
        {filtering && <Skeleton className="h-10 w-64" />}
        <div className="border border-border rounded-lg">
          <div className="p-4 space-y-3">
            {Array.from(
              { length: pagination?.pageSize || 10 },
              (_, i) => `skeleton-row-${i}`,
            ).map((key) => (
              <Skeleton key={key} className="h-12 w-full" />
            ))}
          </div>
        </div>
        {pagination && (
          <div className="flex justify-between items-center">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-48" />
          </div>
        )}
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div
        className={cn("text-center py-8", className)}
        data-testid={`${testId}-error`}
      >
        <div className="text-destructive-foreground mb-2">
          Error loading data
        </div>
        <div className="text-sm text-muted-foreground">{error}</div>
      </div>
    );
  }

  // Check if all rows are selected
  const allSelectableRows = data.filter(
    (row, index) => !selection?.selectable || selection.selectable(row, index),
  );
  const selectedCount = selection?.selectedRows.size || 0;
  const allSelected =
    selectedCount > 0 && selectedCount === allSelectableRows.length;
  const someSelected =
    selectedCount > 0 && selectedCount < allSelectableRows.length;

  return (
    <div className={cn("space-y-4", className)} data-testid={testId}>
      {/* Filter input */}
      {filtering && (
        <div className="flex items-center space-x-2">
          <Input
            placeholder={filtering.placeholder || "Filter data..."}
            value={filtering.value}
            onChange={(e) => filtering.onChange(e.target.value)}
            className="max-w-sm"
            data-testid={`${testId}-filter`}
          />
          {filtering.value && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => filtering.onChange("")}
              data-testid={`${testId}-clear-filter`}
            >
              Clear
            </Button>
          )}
        </div>
      )}

      {/* Table */}
      <div className="border border-border rounded-lg overflow-hidden">
        <table className="w-full" data-testid={`${testId}-table`}>
          <thead className="bg-muted/50">
            <tr>
              {/* Selection column */}
              {selection && (
                <th className="w-12 p-4">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={(input) => {
                      if (input) input.indeterminate = someSelected;
                    }}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-border"
                    data-testid={`${testId}-select-all`}
                  />
                </th>
              )}

              {/* Data columns */}
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={cn(
                    "text-left p-4 font-medium text-foreground",
                    column.sortable && "cursor-pointer hover:bg-muted",
                    column.className,
                  )}
                  style={column.width ? { width: column.width } : undefined}
                  onClick={() =>
                    column.sortable && handleSort(String(column.key))
                  }
                  data-testid={`${testId}-header-${String(column.key)}`}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.title}</span>
                    {column.sortable && sorting && (
                      <span className="text-muted-foreground text-xs">
                        {sorting.config?.key === column.key
                          ? sorting.config.direction === "asc"
                            ? "↑"
                            : "↓"
                          : "↕"}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (selection ? 1 : 0)}
                  className="text-center py-8 text-muted-foreground"
                  data-testid={`${testId}-empty`}
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, index) => {
                const isSelectable =
                  !selection?.selectable || selection.selectable(row, index);
                const isSelected = selection?.selectedRows.has(index) || false;
                // Generate a more stable key using row data or fallback to index
                const getRowId = (item: T): string => {
                  if (
                    "id" in item &&
                    (typeof item.id === "string" || typeof item.id === "number")
                  ) {
                    return String(item.id);
                  }
                  if (
                    "key" in item &&
                    (typeof item.key === "string" ||
                      typeof item.key === "number")
                  ) {
                    return String(item.key);
                  }
                  return `row-${index}`;
                };
                const rowKey = getRowId(row);

                return (
                  <tr
                    key={rowKey}
                    className={cn(
                      "border-t border-border hover:bg-muted/30 transition-colors",
                      isSelected && "bg-muted/50",
                    )}
                    data-testid={`${testId}-row-${index}`}
                  >
                    {/* Selection column */}
                    {selection && (
                      <td className="p-4">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelectable}
                          onChange={(e) =>
                            handleRowSelection(index, e.target.checked)
                          }
                          className="rounded border-border disabled:opacity-50"
                          data-testid={`${testId}-select-${index}`}
                        />
                      </td>
                    )}

                    {/* Data columns */}
                    {columns.map((column) => {
                      const value = row[column.key as keyof T];
                      const cellContent = column.render
                        ? column.render(value, row, index)
                        : value?.toString() || "";

                      return (
                        <td
                          key={String(column.key)}
                          className={cn(
                            "p-4 text-foreground",
                            column.className,
                          )}
                          data-testid={`${testId}-cell-${index}-${String(column.key)}`}
                        >
                          {cellContent}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div
          className="flex items-center justify-between"
          data-testid={`${testId}-pagination`}
        >
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">
              Rows per page:
            </span>
            <select
              value={pagination.pageSize}
              onChange={(e) =>
                pagination.onPageSizeChange(Number(e.target.value))
              }
              className="border border-border rounded px-2 py-1 bg-background text-foreground"
              data-testid={`${testId}-page-size`}
            >
              {PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">
              Page {pagination.page} of{" "}
              {Math.ceil(pagination.total / pagination.pageSize)}
            </span>
            <div className="flex space-x-1">
              <Button
                variant="outline"
                size="sm"
                disabled={pagination.page <= 1}
                onClick={() => pagination.onPageChange(pagination.page - 1)}
                data-testid={`${testId}-prev-page`}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={
                  pagination.page >=
                  Math.ceil(pagination.total / pagination.pageSize)
                }
                onClick={() => pagination.onPageChange(pagination.page + 1)}
                data-testid={`${testId}-next-page`}
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;
