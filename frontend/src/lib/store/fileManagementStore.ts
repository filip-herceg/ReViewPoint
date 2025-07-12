/**
 * File Management Store
 *
 * A Zustand-based store for managing files with:
 * - File listing, searching, filtering, and sorting
 * - Single and bulk file selection
 * - File operations (delete, bulk delete, download)
 * - Error and loading state management
 */

import { create } from "zustand";
import { uploadApiClient } from "@/lib/api/clients/uploads";
import type { FileDict } from "@/lib/api/clients/uploads";
import logger from "@/logger";
import { type ViewMode } from "@/components/file-management/FileToolbar";
import {
  type SortField,
  type SortOrder,
} from "@/components/file-management/FileToolbar";

// File Store Item (enhanced with UI state)
export interface FileItem extends FileDict {
  id?: number;
  filename: string;
  url: string;
  content_type?: string;
  size?: number;
  created_at?: string;
  createdAt?: string; // Alias for created_at for component compatibility
  status?: "uploaded" | "processing" | "error";
  progress?: number;
  selected?: boolean;
}

// Store Configuration
export interface FileManagementConfig {
  itemsPerPage: number;
  /** Items per page (alias for itemsPerPage, for compatibility) */
  pageSize?: number;
  defaultViewMode: ViewMode;
  defaultSort: {
    field: SortField;
    order: SortOrder;
  };
  enabledActions: {
    download: boolean;
    delete: boolean;
    share: boolean;
    bulkActions: boolean;
    search: boolean;
    filter: boolean;
    sort: boolean;
  };
  bulkActionsThreshold: number;
}

// Filter options
export interface FileFilters {
  status: string[];
  contentType: string[];
  sizeRange: { min: number; max: number } | null;
  dateRange: { start: string; end: string } | null;
  userId: number | null;
}

// Error types
export type FileManagementErrorType =
  | "network_error"
  | "server_error"
  | "not_found"
  | "unauthorized"
  | "forbidden"
  | "validation_error";

// Error object
export interface FileManagementError {
  message: string;
  type: FileManagementErrorType;
  details?: any;
}

// File Management Store State
interface FileManagementState {
  // Data
  files: FileItem[];
  totalFiles: number;
  currentPage: number;
  itemsPerPage: number;
  loading: boolean;
  error: FileManagementError | null;

  // Selection
  selectedFiles: string[];

  // Search & Filter
  searchQuery: string;
  filters: FileFilters;
  sortField: SortField;
  sortOrder: SortOrder;
  viewMode: ViewMode;

  // Configuration
  config: FileManagementConfig;

  // Actions
  fetchFiles: (options?: {
    page?: number;
    itemsPerPage?: number;
    search?: string;
    sortField?: SortField;
    sortOrder?: SortOrder;
  }) => Promise<void>;
  refreshFiles: () => Promise<void>;
  deleteFile: (filename: string) => Promise<void>;
  selectFile: (filename: string) => void;
  selectFiles: (filenames: string[]) => void;
  deselectFile: (filename: string) => void;
  deselectFiles: (filenames: string[]) => void;
  clearSelection: () => void;
  selectAllFiles: () => void;
  bulkDownload: (filenames: string[]) => Promise<void>;
  bulkDelete: (
    filenames: string[],
  ) => Promise<{ deleted: string[]; failed: string[] }>;
  bulkShare: (filenames: string[]) => Promise<void>;
  setFilters: (filters: Partial<FileFilters>) => void;
  clearFilters: () => void;
  setSort: (field: SortField, order: SortOrder) => void;
  setViewMode: (mode: ViewMode) => void;
  setSearchQuery: (query: string) => void;
  setPage: (page: number) => void;
  setCurrentPage: (page: number) => void;
  setItemsPerPage: (count: number) => void;
}

// Default configuration
const DEFAULT_CONFIG: FileManagementConfig = {
  itemsPerPage: 25,
  pageSize: 25,
  defaultViewMode: "table",
  defaultSort: {
    field: "created_at",
    order: "desc",
  },
  enabledActions: {
    download: true,
    delete: true,
    share: false,
    bulkActions: true,
    search: true,
    filter: true,
    sort: true,
  },
  bulkActionsThreshold: 500, // Max number of items that can be selected for bulk actions
};

// Default filters
const DEFAULT_FILTERS: FileFilters = {
  status: [],
  contentType: [],
  sizeRange: null,
  dateRange: null,
  userId: null,
};

/**
 * File Management Store Implementation
 */
export const useFileManagementStore = create<FileManagementState>(
  (set, get) => ({
    // Initial state
    files: [],
    totalFiles: 0,
    currentPage: 1,
    itemsPerPage: DEFAULT_CONFIG.itemsPerPage,
    loading: false,
    error: null,

    // Selection state
    selectedFiles: [],

    // Search & Filter state
    searchQuery: "",
    filters: DEFAULT_FILTERS,
    sortField: DEFAULT_CONFIG.defaultSort.field,
    sortOrder: DEFAULT_CONFIG.defaultSort.order,
    viewMode: DEFAULT_CONFIG.defaultViewMode,

    // Configuration
    config: DEFAULT_CONFIG,

    // Actions
    fetchFiles: async (options = {}) => {
      const {
        page = get().currentPage,
        itemsPerPage = get().itemsPerPage,
        search = get().searchQuery,
        sortField = get().sortField,
        sortOrder = get().sortOrder,
      } = options;

      set({ loading: true, error: null });

      try {
        logger.info("🔍 Fetching files", {
          page,
          limit: itemsPerPage,
          search,
          sort: sortField,
          order: sortOrder,
        });

        const result = await uploadApiClient.listFiles({
          limit: itemsPerPage,
          offset: (page - 1) * itemsPerPage,
          q: search || undefined,
          sort:
            sortField === "size" || sortField === "content_type"
              ? "filename"
              : sortField,
          order: sortOrder,
        });

        // Map server response to our FileItem format
        const mappedFiles = result.files.map((file) => ({
          ...file,
          filename: file.filename || "", // Ensure filename exists
          url: file.url || "", // Ensure url exists
          createdAt: new Date().toISOString(), // Default date for compatibility
          status: "uploaded" as const, // Default status
          selected: file.filename
            ? get().selectedFiles.includes(file.filename)
            : false,
        }));

        set({
          files: mappedFiles,
          totalFiles: result.total,
          currentPage: page,
          loading: false,
        });

        logger.info("✅ Files fetched successfully", {
          count: mappedFiles.length,
          total: result.total,
        });
      } catch (error: any) {
        logger.error("❌ Failed to fetch files", error);

        set({
          loading: false,
          error: {
            message: error.message || "Failed to load files",
            type:
              error.response?.status === 404
                ? "not_found"
                : error.response?.status === 401
                  ? "unauthorized"
                  : error.response?.status === 403
                    ? "forbidden"
                    : error.message.includes("network")
                      ? "network_error"
                      : "server_error",
            details: error,
          },
        });
      }
    },

    refreshFiles: async () => {
      // Reset to first page when refreshing
      return get().fetchFiles({ page: 1 });
    },

    deleteFile: async (filename: string) => {
      try {
        logger.info("🗑️ Deleting file", { filename });

        await uploadApiClient.deleteFile(filename);

        // Remove from UI state
        set((state) => ({
          files: state.files.filter((f) => f.filename !== filename),
          totalFiles: Math.max(0, state.totalFiles - 1),
          selectedFiles: state.selectedFiles.filter((f) => f !== filename),
        }));

        logger.info("✅ File deleted successfully", { filename });
      } catch (error: any) {
        logger.error("❌ Failed to delete file", { filename, error });

        throw error;
      }
    },

    selectFile: (filename: string) => {
      set((state) => {
        // Don't add duplicates
        if (state.selectedFiles.includes(filename)) {
          return state;
        }

        // Update selected files array and mark file as selected
        return {
          selectedFiles: [...state.selectedFiles, filename],
          files: state.files.map((file) =>
            file.filename === filename ? { ...file, selected: true } : file,
          ),
        };
      });
    },

    selectFiles: (filenames: string[]) => {
      set((state) => {
        // Filter out any already selected files to avoid duplicates
        const newFilenames = filenames.filter(
          (filename) => !state.selectedFiles.includes(filename),
        );

        if (newFilenames.length === 0) {
          return state;
        }

        // Update selected files array and mark files as selected
        return {
          selectedFiles: [...state.selectedFiles, ...newFilenames],
          files: state.files.map((file) =>
            filenames.includes(file.filename)
              ? { ...file, selected: true }
              : file,
          ),
        };
      });
    },

    deselectFile: (filename: string) => {
      set((state) => ({
        selectedFiles: state.selectedFiles.filter((f) => f !== filename),
        files: state.files.map((file) =>
          file.filename === filename ? { ...file, selected: false } : file,
        ),
      }));
    },

    deselectFiles: (filenames: string[]) => {
      set((state) => ({
        selectedFiles: state.selectedFiles.filter(
          (f) => !filenames.includes(f),
        ),
        files: state.files.map((file) =>
          filenames.includes(file.filename)
            ? { ...file, selected: false }
            : file,
        ),
      }));
    },

    clearSelection: () => {
      set((state) => ({
        selectedFiles: [],
        files: state.files.map((file) => ({ ...file, selected: false })),
      }));
    },

    selectAllFiles: () => {
      set((state) => {
        const allFilenames = state.files.map((file) => file.filename);
        return {
          selectedFiles: allFilenames,
          files: state.files.map((file) => ({ ...file, selected: true })),
        };
      });
    },

    bulkDownload: async (filenames: string[]) => {
      logger.info("📥 Starting bulk download", { count: filenames.length });

      try {
        // Process files sequentially to avoid overwhelming browser
        for (const filename of filenames) {
          const blob = await uploadApiClient.downloadFile(filename);

          // Create download link
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();

          // Clean up
          document.body.removeChild(a);
          URL.revokeObjectURL(url);

          logger.info("✅ Downloaded file", { filename });
        }
      } catch (error: any) {
        logger.error("❌ Bulk download failed", error);
        throw error;
      }
    },

    bulkDelete: async (filenames: string[]) => {
      if (!filenames.length) {
        return { deleted: [], failed: [] };
      }

      logger.info("🗑️ Starting bulk delete", { count: filenames.length });

      try {
        const result = await uploadApiClient.bulkDeleteFiles(filenames);

        // Update UI state for successfully deleted files
        set((state) => ({
          files: state.files.filter(
            (f) => !result.deleted.includes(f.filename),
          ),
          totalFiles: Math.max(0, state.totalFiles - result.deleted.length),
          selectedFiles: state.selectedFiles.filter(
            (f) => !result.deleted.includes(f),
          ),
        }));

        logger.info("✅ Bulk delete completed", {
          deleted: result.deleted.length,
          failed: result.failed.length,
        });

        return result;
      } catch (error: any) {
        logger.error("❌ Bulk delete failed", error);
        throw error;
      }
    },

    bulkShare: async (filenames: string[]) => {
      logger.info("🔗 Sharing files", { files: filenames });
      // Placeholder for future share implementation
      // Could generate shareable links via API
      return Promise.resolve();
    },

    setFilters: (filters: Partial<FileFilters>) => {
      set((state) => ({
        filters: { ...state.filters, ...filters },
        // Reset to first page when filters change
        currentPage: 1,
      }));

      // Re-fetch with new filters
      get().fetchFiles({ page: 1 });
    },

    clearFilters: () => {
      set({ filters: DEFAULT_FILTERS });
      // Re-fetch with cleared filters
      get().fetchFiles({ page: 1 });
    },

    setSort: (field: SortField, order: SortOrder) => {
      set({ sortField: field, sortOrder: order });
      // Re-fetch with new sort
      get().fetchFiles({ sortField: field, sortOrder: order, page: 1 });
    },

    setViewMode: (mode: ViewMode) => {
      set({ viewMode: mode });
    },

    setSearchQuery: (query: string) => {
      set({ searchQuery: query });
      // Re-fetch with new search query (debounced in UI)
      get().fetchFiles({ search: query, page: 1 });
    },

    setPage: (page: number) => {
      // Alias for setCurrentPage
      get().setCurrentPage(page);
    },

    setCurrentPage: (page: number) => {
      set({ currentPage: page });
      // Re-fetch with new page
      get().fetchFiles({ page });
    },

    setItemsPerPage: (count: number) => {
      set({ itemsPerPage: count });
      // Re-fetch with new items per page
      get().fetchFiles({ itemsPerPage: count, page: 1 });
    },
  }),
);

// Utility functions
export function createTestFileManagementConfig(): FileManagementConfig {
  return DEFAULT_CONFIG;
}

export function createTestFileItem(
  overrides: Partial<FileItem> = {},
): FileItem {
  return {
    filename: `test-${Math.random().toString(36).substring(2, 7)}.pdf`,
    url: `https://example.com/files/test-file.pdf`,
    content_type: "application/pdf",
    size: 12345,
    created_at: new Date().toISOString(),
    createdAt: new Date().toISOString(),
    status: "uploaded",
    ...overrides,
  };
}

export function createTestFileManagementState(
  overrides: Partial<FileManagementState> = {},
) {
  const store = useFileManagementStore.getState();
  return {
    ...store,
    ...overrides,
  };
}
