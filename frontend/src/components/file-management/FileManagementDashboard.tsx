import React, { useEffect, useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import logger from '@/logger';
import { useFileManagementStore } from '@/lib/store/fileManagementStore';
import {
    FileTable,
    FileGrid,
    FileList,
    FileToolbar,
    FileBulkActions,
    FilePreviewModal,
    FileSearchFilters,
    type ViewMode,
    type SortField,
    type SortOrder,
    type FileFilters
} from '.';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    RefreshCw,
    FileText,
    AlertCircle,
    FileX,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react';

// Define FileItem type locally to match what's in the store
interface FileItem {
    filename: string;
    url: string;
    status?: string;
    progress?: number;
    createdAt?: string;
}

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
export const FileManagementDashboard: React.FC<FileManagementDashboardProps> = ({
    className,
}) => {
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
        setPage,
        setCurrentPage,
        setItemsPerPage,
    } = useFileManagementStore();

    // Local state
    const [searchQuery, setSearchQuery] = useState('');
    const [sortField, setSortField] = useState<SortField>('created_at');
    const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
    const [showFilters, setShowFilters] = useState(false);
    const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
    const [deleteConfirmFile, setDeleteConfirmFile] = useState<FileItem | null>(null);
    const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [filters, setFilters] = useState<FileFilters>({
        status: [],
        contentType: [],
        sizeRange: null,
        dateRange: null,
        userId: null,
    });

    // Effects
    useEffect(() => {
        logger.info('File Management Dashboard mounted, fetching initial files');
        fetchFiles();
    }, [fetchFiles]);

    // Filter and sort files
    const filteredAndSortedFiles = React.useMemo(() => {
        let result = [...files];

        // Apply search filter
        if (searchQuery) {
            result = result.filter(file =>
                file.filename.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        // Apply status filter
        if (filters.status.length > 0) {
            result = result.filter(file =>
                file.status && filters.status.includes(file.status)
            );
        }

        // Apply content type filter (simplified since we don't have content_type)
        if (filters.contentType.length > 0) {
            result = result.filter(file => {
                const extension = file.filename.split('.').pop()?.toLowerCase() || '';
                return filters.contentType.some((type: string) => {
                    if (type.includes('pdf')) return extension === 'pdf';
                    if (type.includes('image')) return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension);
                    if (type.includes('text')) return ['txt', 'md', 'csv'].includes(extension);
                    if (type.includes('word')) return ['doc', 'docx'].includes(extension);
                    if (type.includes('excel')) return ['xls', 'xlsx'].includes(extension);
                    if (type.includes('powerpoint')) return ['ppt', 'pptx'].includes(extension);
                    return false;
                });
            });
        }

        // Skip size filter since we don't have size info
        // Skip date filter since we only have createdAt (optional)
        // Skip user filter since we don't have user_id

        // Sort files
        result.sort((a, b) => {
            let aValue: any, bValue: any;

            switch (sortField) {
                case 'filename':
                    aValue = a.filename.toLowerCase();
                    bValue = b.filename.toLowerCase();
                    break;
                case 'created_at':
                    aValue = new Date(a.createdAt || '');
                    bValue = new Date(b.createdAt || '');
                    break;
                case 'content_type':
                    // We don't have content_type directly, so use a derived type from filename
                    aValue = a.filename.split('.').pop()?.toLowerCase() || '';
                    bValue = b.filename.split('.').pop()?.toLowerCase() || '';
                    break;
                case 'size':
                    // We don't have size data, so default to 0
                    aValue = 0;
                    bValue = 0;
                    break;
                default:
                    return 0;
            }

            if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
            if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
            return 0;
        });

        return result;
    }, [files, searchQuery, filters, sortField, sortOrder]);

    // Handlers
    const handleRefresh = useCallback(async () => {
        logger.info('Refreshing file list');
        await refreshFiles();
    }, [refreshFiles]);

    const handleSearchChange = useCallback((query: string) => {
        logger.debug('Searching files:', query);
        setSearchQuery(query);
        // Also call the store method if it exists (for testing and future functionality)
        if (storeSetSearchQuery) {
            storeSetSearchQuery(query);
        }
    }, [storeSetSearchQuery]);

    const handleSortChange = useCallback((field: SortField, order: SortOrder) => {
        logger.debug('Changing sort:', { field, order });
        setSortField(field);
        setSortOrder(order);
        // Also call the store method for testing and future functionality
        if (setSort) {
            setSort(field, order);
        }
    }, [setSort]);

    const handleFilePreview = useCallback((file: FileItem) => {
        logger.debug('Opening file preview:', file.filename);
        setPreviewFile(file);
    }, []);

    const handleClosePreview = useCallback(() => {
        logger.debug('Closing file preview');
        setPreviewFile(null);
    }, []);

    const handleFileDelete = useCallback(async (file: FileItem) => {
        // Show confirmation dialog first
        setDeleteConfirmFile(file);
        setIsDeleteConfirmOpen(true);
    }, []);

    const handleConfirmDelete = useCallback(async () => {
        if (!deleteConfirmFile) return;

        logger.info('Deleting file:', deleteConfirmFile.filename);
        try {
            await deleteFile(deleteConfirmFile.filename);
            logger.info('File deleted successfully:', deleteConfirmFile.filename);
        } catch (error) {
            logger.error('Error deleting file:', error);
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
            const link = document.createElement('a');
            link.href = file.url;
            link.download = file.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            logger.error('Error downloading file:', error);
        }
    }, []);

    const handleFileShare = useCallback(async (file: FileItem) => {
        logger.info('Sharing file:', file.filename);
        try {
            if (navigator.share) {
                await navigator.share({
                    title: file.filename,
                    url: file.url,
                });
            } else {
                // Fallback: copy URL to clipboard
                await navigator.clipboard.writeText(file.url);
                alert('File URL copied to clipboard!');
            }
        } catch (error) {
            logger.error('Error sharing file:', error);
        }
    }, []);

    const handleSelectionChange = useCallback((filename: string, selected: boolean) => {
        if (selected) {
            selectFile(filename);
        } else {
            deselectFile(filename);
        }
    }, [selectFile, deselectFile]);

    const handleSelectAll = useCallback((selected: boolean) => {
        if (selected) {
            selectAllFiles();
        } else {
            clearSelection();
        }
    }, [selectAllFiles, clearSelection]);

    // Bulk operation handlers
    const handleBulkDownload = useCallback(async () => {
        logger.info('Bulk downloading files:', selectedFiles);
        const filesToDownload = files.filter(f => selectedFiles.includes(f.filename));
        for (const file of filesToDownload) {
            try {
                const link = document.createElement('a');
                link.href = file.url;
                link.download = file.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                // Add small delay between downloads
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (error) {
                logger.error('Error downloading file:', file.filename, error);
            }
        }
    }, [selectedFiles, files]);

    const handleBulkShare = useCallback(async () => {
        logger.info('Bulk sharing files:', selectedFiles);
        // Implement bulk share logic
    }, [selectedFiles]);

    const handleBulkDelete = useCallback(async () => {
        logger.info('Bulk deleting files:', selectedFiles);
        for (const filename of selectedFiles) {
            try {
                await deleteFile(filename);
            } catch (error) {
                logger.error('Error deleting file:', filename, error);
            }
        }
        clearSelection();
    }, [selectedFiles, deleteFile, clearSelection]);

    const handleBulkArchive = useCallback(async () => {
        logger.info('Bulk archiving files:', selectedFiles);
        // Implement bulk archive logic
    }, [selectedFiles]);

    const handleBulkMove = useCallback(async () => {
        logger.info('Bulk moving files:', selectedFiles);
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
                    {Array.from({ length: 5 }).map((_, i) => (
                        <div key={i} className="flex items-center space-x-4 animate-pulse">
                            <div className="h-10 w-10 bg-gray-200 rounded" />
                            <div className="flex-1 space-y-2">
                                <div className="h-4 bg-gray-200 rounded w-full" />
                                <div className="h-3 bg-gray-200 rounded w-1/2" />
                            </div>
                            <div className="h-8 w-20 bg-gray-200 rounded" />
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );

    // Render error state
    const renderErrorState = () => (
        <Card className="w-full">
            <CardContent className="flex flex-col items-center justify-center py-16">
                <AlertCircle className="h-16 w-16 text-red-500 mb-4" />
                <CardTitle className="mb-2">Failed to load files</CardTitle>
                <p className="text-gray-600 text-center mb-6">
                    {error?.message || 'An error occurred while loading your files. Please try again.'}
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
                <FileX className="h-16 w-16 text-gray-300 mb-4" />
                <CardTitle className="mb-2">
                    {searchQuery || Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true))
                        ? 'No matching files found'
                        : 'No files uploaded yet'
                    }
                </CardTitle>
                <p className="text-gray-600 text-center mb-6">
                    {searchQuery || Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true))
                        ? 'Try adjusting your search terms or filters.'
                        : 'Upload your first file to get started.'
                    }
                </p>
                {(searchQuery || Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true))) && (
                    <Button
                        variant="outline"
                        onClick={() => {
                            setSearchQuery('');
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
            case 'table':
                return (
                    <FileTable
                        {...commonProps}
                        onSelectAll={handleSelectAll}
                    />
                );
            case 'grid':
                return <FileGrid {...commonProps} />;
            case 'list':
                return <FileList {...commonProps} />;
            default:
                return (
                    <FileTable
                        {...commonProps}
                        onSelectAll={handleSelectAll}
                    />
                );
        }
    };

    return (
        <main className={cn('w-full space-y-6', className)} role="main">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">File Management</h1>
                    <p className="text-gray-600">
                        Manage and organize your uploaded files
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600">
                            {totalFiles} total files
                        </span>
                    </div>
                    {hasSelection && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                            {selectedCount} selected
                        </span>
                    )}
                </div>
            </div>

            {/* Toolbar */}
            <FileToolbar
                searchQuery={searchQuery}
                onSearchChange={handleSearchChange}
                viewMode={viewMode}
                onViewModeChange={setViewMode}
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
                onClearFilters={() => setFilters({
                    status: [],
                    contentType: [],
                    sizeRange: null,
                    dateRange: null,
                    userId: null,
                })}
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
            {loading && !hasFiles ? (
                renderLoadingState()
            ) : error ? (
                renderErrorState()
            ) : !hasFiles && !loading ? (
                renderEmptyState()
            ) : (
                renderFileContent()
            )}

            {/* Pagination Controls */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-white border-t">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>
                        Page {currentPage} of {Math.ceil(totalFiles / config.pageSize)}
                    </span>
                    <div className="flex items-center gap-2">
                        <span>Items per page:</span>
                        <div className="relative">
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    const menu = e.currentTarget.nextElementSibling as HTMLElement;
                                    if (menu) {
                                        menu.classList.toggle('hidden');
                                    }
                                }}
                                className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white min-w-[60px] text-left"
                                role="combobox"
                                aria-label="Items per page"
                                aria-expanded="false"
                                aria-haspopup="listbox"
                            >
                                {config.pageSize}
                            </button>
                            <div className="hidden absolute left-0 mt-1 w-20 bg-white rounded-md shadow-lg border border-gray-200 z-10" role="listbox">
                                <div className="py-1">
                                    {[10, 20, 50, 100].map((size) => (
                                        <button
                                            key={size}
                                            className={cn(
                                                'flex items-center w-full px-3 py-2 text-sm hover:bg-gray-100',
                                                config.pageSize === size ? 'text-blue-600 bg-blue-50' : 'text-gray-700'
                                            )}
                                            onClick={() => {
                                                setItemsPerPage(size);
                                                // Close the dropdown
                                                const menu = document.querySelector('[role="listbox"]') as HTMLElement;
                                                if (menu) menu.classList.add('hidden');
                                            }}
                                            role="option"
                                            aria-selected={config.pageSize === size}
                                        >
                                            {size}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setCurrentPage(currentPage - 1)}
                        disabled={currentPage === 1}
                        aria-label="Previous page"
                        className="inline-flex items-center justify-center h-9 w-9 rounded-md border border-gray-300 text-gray-500 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </button>

                    <span className="px-3 py-1 text-sm text-gray-600">
                        Page {currentPage}
                    </span>

                    <button
                        onClick={() => setCurrentPage(currentPage + 1)}
                        disabled={currentPage >= Math.ceil(totalFiles / config.pageSize)}
                        aria-label="Next page"
                        className="inline-flex items-center justify-center h-9 w-9 rounded-md border border-gray-300 text-gray-500 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronRight className="h-4 w-4" />
                    </button>
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
                    <div className="bg-white rounded-lg shadow-xl max-w-md w-full m-4 p-6">
                        <h2 id="delete-confirm-title" className="text-lg font-semibold text-gray-900 mb-2">
                            Confirm Delete
                        </h2>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to delete "{deleteConfirmFile.filename}"? This action cannot be undone.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={handleCancelDelete}
                                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleConfirmDelete}
                                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
                            >
                                Confirm
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
};
