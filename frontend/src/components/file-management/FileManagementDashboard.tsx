import {
	AlertCircle,
	ChevronLeft,
	ChevronRight,
	FileText,
	FileX,
	RefreshCw,
} from "lucide-react";
import React, { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
// Define FileItem type locally to match what's in the store
import type { FileItem as StoreFileItem } from "@/lib/store/fileManagementStore";
import { useFileManagementStore } from "@/lib/store/fileManagementStore";
import { cn } from "@/lib/utils";
import logger from "@/logger";
import {
	FileBulkActions,
	type FileFilters,
	FileGrid,
	FileList,
	FilePreviewModal,
	FileSearchFilters,
	FileTable,
	FileToolbar,
	type SortField,
	type SortOrder,
} from ".";

type FileItem = StoreFileItem;

interface FileManagementDashboardProps {
	className?: string;
}

/**
 * File Management Dashboard Component
 *
 * Main dashboard component for managing files with advanced features:
 * - Multiple view modes (table, grid, list)
 * - Search and filtering
 * - Bulk operations
 * - File preview
 * - Real-time updates
 * - Pagination
 */
export const FileManagementDashboard: React.FC<
	FileManagementDashboardProps
> = ({ className }) => {
	// Store hooks
	const {
		files,
		totalFiles,
		currentPage,
		config,
		loading,
		error,
		selectedFiles,
		viewMode,
		fetchFiles,
		refreshFiles,
		deleteFile,
		clearSelection,
		selectFile,
		deselectFile,
		selectAllFiles,
		setViewMode,
		setSearchQuery: storeSetSearchQuery,
		setSort,
		setCurrentPage,
		setItemsPerPage,
	} = useFileManagementStore();

	// Ensure all FileItem.status values are valid for downstream components
	const normalizedFiles = files.map((f) => ({
		...f,
		status:
			f.status === "uploaded" ||
			f.status === "processing" ||
			f.status === "error"
				? f.status
				: "uploaded",
	}));

	// Local state
	const [searchQuery, setSearchQuery] = useState("");
	const [sortField, setSortField] = useState<SortField>("created_at");
	const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
	const [showFilters, setShowFilters] = useState(false);
	const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
	const [deleteConfirmFile, setDeleteConfirmFile] = useState<FileItem | null>(
		null,
	);
	const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
	const [_isFilterModalOpen, _setIsFilterModalOpen] = useState(false);
	const [filters, setFilters] = useState<FileFilters>({
		status: [],
		contentType: [],
		sizeRange: null,
		dateRange: null,
		userId: null,
	});

	// Effects
	useEffect(() => {
		logger.info("File Management Dashboard mounted, fetching initial files");
		fetchFiles();
	}, [fetchFiles]);

	// Filter and sort files
	const filteredAndSortedFiles = React.useMemo(() => {
		let result = [...normalizedFiles];

		// Apply search filter
		if (searchQuery) {
			result = result.filter((file) =>
				file.filename.toLowerCase().includes(searchQuery.toLowerCase()),
			);
		}

		// Apply status filter
		if (filters.status.length > 0) {
			result = result.filter(
				(file) => file.status && filters.status.includes(file.status),
			);
		}

		// Apply content type filter (simplified since we don't have content_type)
		if (filters.contentType.length > 0) {
			result = result.filter((file) => {
				const extension = file.filename.split(".").pop()?.toLowerCase() || "";
				return filters.contentType.some((type: string) => {
					if (type.includes("pdf")) return extension === "pdf";
					if (type.includes("image"))
						return ["jpg", "jpeg", "png", "gif", "webp"].includes(extension);
					if (type.includes("text"))
						return ["txt", "md", "csv"].includes(extension);
					if (type.includes("word")) return ["doc", "docx"].includes(extension);
					if (type.includes("excel"))
						return ["xls", "xlsx"].includes(extension);
					if (type.includes("powerpoint"))
						return ["ppt", "pptx"].includes(extension);
					return false;
				});
			});
		}

		// Skip size filter since we don't have size info
		// Skip date filter since we only have createdAt (optional)
		// Skip user filter since we don't have user_id

		// Sort files
		result.sort((a, b) => {
			let aValue: string | number | Date, bValue: string | number | Date;

			switch (sortField) {
				case "filename":
					aValue = a.filename.toLowerCase();
					bValue = b.filename.toLowerCase();
					break;
				case "created_at":
					aValue = new Date(a.createdAt || "");
					bValue = new Date(b.createdAt || "");
					break;
				case "content_type":
					// We don't have content_type directly, so use a derived type from filename
					aValue = a.filename.split(".").pop()?.toLowerCase() || "";
					bValue = b.filename.split(".").pop()?.toLowerCase() || "";
					break;
				case "size":
					// We don't have size data, so default to 0
					aValue = 0;
					bValue = 0;
					break;
				default:
					return 0;
			}

			if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
			if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
			return 0;
		});

		return result;
	}, [searchQuery, filters, sortField, sortOrder, normalizedFiles]);

	// Handlers
	const handleRefresh = useCallback(async () => {
		logger.info("Refreshing file list");
		await refreshFiles();
	}, [refreshFiles]);

	const handleSearchChange = useCallback(
		(query: string) => {
			logger.debug("Searching files:", query);
			setSearchQuery(query);
			// Also call the store method if it exists (for testing and future functionality)
			if (storeSetSearchQuery) {
				storeSetSearchQuery(query);
			}
		},
		[storeSetSearchQuery],
	);

	const handleSortChange = useCallback(
		(field: SortField, order: SortOrder) => {
			logger.debug("Changing sort:", { field, order });
			setSortField(field);
			setSortOrder(order);
			// Also call the store method for testing and future functionality
			if (setSort) {
				setSort(field, order);
			}
		},
		[setSort],
	);

	const handleFilePreview = useCallback((file: FileItem) => {
		logger.debug("Opening file preview:", file.filename);
		setPreviewFile(file);
	}, []);

	const handleClosePreview = useCallback(() => {
		logger.debug("Closing file preview");
		setPreviewFile(null);
	}, []);

	const handleFileDelete = useCallback(async (file: FileItem) => {
		// Show confirmation dialog first
		setDeleteConfirmFile(file);
		setIsDeleteConfirmOpen(true);
	}, []);

	const handleConfirmDelete = useCallback(async () => {
		if (!deleteConfirmFile) return;

		logger.info("Deleting file:", deleteConfirmFile.filename);
		try {
			await deleteFile(deleteConfirmFile.filename);
			logger.info("File deleted successfully:", deleteConfirmFile.filename);
		} catch (error) {
			logger.error("Error deleting file:", error);
		} finally {
			setDeleteConfirmFile(null);
			setIsDeleteConfirmOpen(false);
		}
	}, [deleteFile, deleteConfirmFile]);

	const handleCancelDelete = useCallback(() => {
		setDeleteConfirmFile(null);
		setIsDeleteConfirmOpen(false);
	}, []);

	const handleFileDownload = useCallback(async (file: FileItem) => {
		logger.debug(`Downloading file: ${file.filename}`, { file });
		try {
			// Create a download link using the file URL
			const link = document.createElement("a");
			link.href = file.url;
			link.download = file.filename;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		} catch (error) {
			logger.error("Error downloading file:", error);
		}
	}, []);

	const handleFileShare = useCallback(async (file: FileItem) => {
		logger.info("Sharing file:", file.filename);
		try {
			if (navigator.share) {
				await navigator.share({
					title: file.filename,
					url: file.url,
				});
			} else {
				// Fallback: copy URL to clipboard
				await navigator.clipboard.writeText(file.url);
				alert("File URL copied to clipboard!");
			}
		} catch (error) {
			logger.error("Error sharing file:", error);
		}
	}, []);

	const handleSelectionChange = useCallback(
		(filename: string, selected: boolean) => {
			if (selected) {
				selectFile(filename);
			} else {
				deselectFile(filename);
			}
		},
		[selectFile, deselectFile],
	);

	const handleSelectAll = useCallback(
		(selected: boolean) => {
			if (selected) {
				selectAllFiles();
			} else {
				clearSelection();
			}
		},
		[selectAllFiles, clearSelection],
	);

	// Bulk operation handlers
	const handleBulkDownload = useCallback(async () => {
		logger.info("Bulk downloading files:", selectedFiles);
		const filesToDownload = files.filter((f) =>
			selectedFiles.includes(f.filename),
		);
		for (const file of filesToDownload) {
			try {
				const link = document.createElement("a");
				link.href = file.url;
				link.download = file.filename;
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				// Add small delay between downloads
				await new Promise((resolve) => setTimeout(resolve, 100));
			} catch (error) {
				logger.error("Error downloading file:", file.filename, error);
			}
		}
	}, [selectedFiles, files]);

	const handleBulkShare = useCallback(async () => {
		logger.info("Bulk sharing files:", selectedFiles);
		// Implement bulk share logic
	}, [selectedFiles]);

	const handleBulkDelete = useCallback(async () => {
		logger.info("Bulk deleting files:", selectedFiles);
		for (const filename of selectedFiles) {
			try {
				await deleteFile(filename);
			} catch (error) {
				logger.error("Error deleting file:", filename, error);
			}
		}
		clearSelection();
	}, [selectedFiles, deleteFile, clearSelection]);

	const handleBulkArchive = useCallback(async () => {
		logger.info("Bulk archiving files:", selectedFiles);
		// Implement bulk archive logic
	}, [selectedFiles]);

	const handleBulkMove = useCallback(async () => {
		logger.info("Bulk moving files:", selectedFiles);
		// Implement bulk move logic
	}, [selectedFiles]);

	// Computed values
	const hasFiles = filteredAndSortedFiles.length > 0;
	const selectedCount = selectedFiles.length;
	const hasSelection = selectedCount > 0;

	// Render loading state
	const renderLoadingState = () => (
		<Card className="w-full">
			<CardContent className="p-6">
				<div className="space-y-4">
					<div className="sr-only" aria-live="polite">
						Loading files...
					</div>
					{Array.from({ length: 5 }, (_, i) => `loading-skeleton-${i}`).map(
						(key) => (
							<div
								key={key}
								className="flex items-center space-x-4 animate-pulse"
							>
								<div className="h-10 w-10 bg-muted rounded" />
								<div className="flex-1 space-y-2">
									<div className="h-4 bg-muted rounded w-full" />
									<div className="h-3 bg-muted rounded w-1/2" />
								</div>
								<div className="h-8 w-20 bg-muted rounded" />
							</div>
						),
					)}
				</div>
			</CardContent>
		</Card>
	);

	// Render error state
	const renderErrorState = () => (
		<Card className="w-full">
			<CardContent className="flex flex-col items-center justify-center py-16">
				<AlertCircle className="h-16 w-16 text-destructive mb-4" />
				<CardTitle className="mb-2">Failed to load files</CardTitle>
				<p className="text-muted-foreground text-center mb-6">
					{error?.message ||
						"An error occurred while loading your files. Please try again."}
				</p>
				<Button onClick={handleRefresh}>
					<RefreshCw className="h-4 w-4 mr-2" />
					Try Again
				</Button>
			</CardContent>
		</Card>
	);

	// Render empty state
	const renderEmptyState = () => (
		<Card className="w-full">
			<CardContent className="flex flex-col items-center justify-center py-16">
				<FileX className="h-16 w-16 text-muted mb-4" />
				<CardTitle className="mb-2">
					{searchQuery ||
					Object.values(filters).some(
						(f) => f && (Array.isArray(f) ? f.length > 0 : true),
					)
						? "No matching files found"
						: "No files uploaded yet"}
				</CardTitle>
				<p className="text-muted-foreground text-center mb-6">
					{searchQuery ||
					Object.values(filters).some(
						(f) => f && (Array.isArray(f) ? f.length > 0 : true),
					)
						? "Try adjusting your search terms or filters."
						: "Upload your first file to get started."}
				</p>
				{(searchQuery ||
					Object.values(filters).some(
						(f) => f && (Array.isArray(f) ? f.length > 0 : true),
					)) && (
					<Button
						variant="outline"
						onClick={() => {
							setSearchQuery("");
							setFilters({
								status: [],
								contentType: [],
								sizeRange: null,
								dateRange: null,
								userId: null,
							});
						}}
					>
						Clear Search & Filters
					</Button>
				)}
			</CardContent>
		</Card>
	);

	// Render file content based on view mode
	const renderFileContent = () => {
		const commonProps = {
			files: filteredAndSortedFiles,
			selectedFiles,
			onSelectionChange: handleSelectionChange,
			onPreview: handleFilePreview,
			onDownload: handleFileDownload,
			onShare: handleFileShare,
			onDelete: handleFileDelete,
			loading,
		};

		switch (viewMode) {
			case "table":
				return <FileTable {...commonProps} onSelectAll={handleSelectAll} />;
			case "grid":
				return <FileGrid {...commonProps} />;
			case "list":
				return <FileList {...commonProps} />;
			default:
				return <FileTable {...commonProps} onSelectAll={handleSelectAll} />;
		}
	};

	return (
		<main className={cn("w-full space-y-6", className)}>
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">File Management</h1>
					<p className="text-gray-600">
						Manage and organize your uploaded files
					</p>
				</div>

				{/* Quick Stats */}
				<div className="flex items-center space-x-2">
					<div className="flex items-center space-x-2">
						<FileText className="h-4 w-4 text-muted-foreground" />
						<span className="text-sm text-muted-foreground">
							{totalFiles} total files
						</span>
					</div>
				</div>
			</div>

			{/* File Toolbar */}
			<FileToolbar
				viewMode={viewMode}
				onViewModeChange={setViewMode}
				searchQuery={searchQuery}
				onSearchChange={handleSearchChange}
				sortField={sortField}
				sortOrder={sortOrder}
				onSortChange={handleSortChange}
				onRefresh={handleRefresh}
				onShowFilters={() => setShowFilters(true)}
				totalFiles={totalFiles}
				selectedCount={selectedCount}
				isRefreshing={loading}
			/>

			{/* Filters Panel */}
			<FileSearchFilters
				isOpen={showFilters}
				onClose={() => setShowFilters(false)}
				filters={filters}
				onFiltersChange={setFilters}
				onClearFilters={() =>
					setFilters({
						status: [],
						contentType: [],
						sizeRange: null,
						dateRange: null,
						userId: null,
					})
				}
				totalFiles={totalFiles}
				filteredFiles={filteredAndSortedFiles.length}
			/>

			{/* Bulk Actions */}
			<FileBulkActions
				selectedCount={selectedCount}
				onDownloadSelected={handleBulkDownload}
				onShareSelected={handleBulkShare}
				onDeleteSelected={handleBulkDelete}
				onArchiveSelected={handleBulkArchive}
				onMoveSelected={handleBulkMove}
				onClearSelection={clearSelection}
				isVisible={hasSelection}
				isLoading={loading}
			/>

			{/* Main Content */}
			{loading && !hasFiles
				? renderLoadingState()
				: error
					? renderErrorState()
					: !hasFiles && !loading
						? renderEmptyState()
						: renderFileContent()}

			{/* Pagination Controls */}
			<div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-background border-t border-border">
				<div className="flex items-center gap-4 text-sm text-muted-foreground">
					<span>
						Page {currentPage} of{" "}
						{Math.ceil(
							totalFiles / (config.pageSize ?? config.itemsPerPage ?? 25),
						)}
					</span>
					<div className="flex items-center gap-2">
						<span>Items per page:</span>
						<div className="relative">
							{" "}
							<select
								value={config.pageSize ?? config.itemsPerPage ?? 25}
								onChange={(e) => setItemsPerPage(Number(e.target.value))}
								className="border border-border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-info bg-background min-w-[60px]"
								aria-label="Items per page"
							>
								{[10, 20, 50, 100].map((size) => (
									<option key={size} value={size}>
										{size}
									</option>
								))}
							</select>
						</div>
					</div>
				</div>

				<div className="flex items-center gap-2">
					<Button
						variant="outline"
						size="icon"
						onClick={() => setCurrentPage(currentPage - 1)}
						disabled={currentPage === 1}
						aria-label="Previous page"
					>
						<ChevronLeft className="h-4 w-4" />
					</Button>
					<span className="px-3 py-1 text-sm text-muted-foreground">
						Page {currentPage}
					</span>
					<Button
						variant="outline"
						size="icon"
						onClick={() => setCurrentPage(currentPage + 1)}
						disabled={
							currentPage >=
							Math.ceil(
								totalFiles / (config.pageSize ?? config.itemsPerPage ?? 25),
							)
						}
						aria-label="Next page"
					>
						<ChevronRight className="h-4 w-4" />
					</Button>
				</div>
			</div>

			{/* File Preview Modal */}
			{previewFile && (
				<FilePreviewModal
					file={previewFile}
					isOpen={!!previewFile}
					onClose={handleClosePreview}
					onDownload={handleFileDownload}
					onShare={handleFileShare}
					onDelete={handleFileDelete}
				/>
			)}

			{/* Delete Confirmation Dialog */}
			{isDeleteConfirmOpen && deleteConfirmFile && (
				<div
					className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
					role="dialog"
					aria-labelledby="delete-confirm-title"
					aria-modal="true"
				>
					<div className="bg-background rounded-lg shadow-xl max-w-md w-full m-4 p-6 border border-border">
						<h2
							id="delete-confirm-title"
							className="text-lg font-semibold text-foreground mb-2"
						>
							Confirm Delete
						</h2>
						<p className="text-muted-foreground mb-6">
							Are you sure you want to delete "{deleteConfirmFile.filename}"?
							This action cannot be undone.
						</p>
						<div className="flex gap-3 justify-end">
							<Button
								variant="outline"
								onClick={handleCancelDelete}
							>
								Cancel
							</Button>
							<Button
								variant="destructive"
								onClick={handleConfirmDelete}
							>
								Confirm
							</Button>
						</div>
					</div>
				</div>
			)}
		</main>
	);
};
