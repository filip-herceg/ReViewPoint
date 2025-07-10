import React from 'react';
import { FileText, Download, Share2, Trash2, Eye, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { formatFileSize, getFileTypeGroup } from '@/lib/utils/fileUtils';

// Get file size utility (placeholder since size is not in FileItem)
const getFileSize = (file: FileItem): number => {
    // Since the FileItem doesn't include size, we'll return 0
    // In a real implementation, this would come from the API
    return 0;
};

// Get content type from filename
const getContentType = (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase() || '';
    const mimeTypes: Record<string, string> = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    };
    return mimeTypes[extension] || 'application/octet-stream';
};

// Define FileItem type to match the store
import type { FileItem as StoreFileItem } from '@/lib/store/fileManagementStore';
type FileItem = StoreFileItem;

interface FileGridProps {
    files: FileItem[];
    selectedFiles: string[];
    onSelectionChange: (fileId: string, selected: boolean) => void;
    onPreview: (file: FileItem) => void;
    onDownload: (file: FileItem) => void;
    onShare: (file: FileItem) => void;
    onDelete: (file: FileItem) => void;
    loading?: boolean;
}

const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase() || '';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
        return '🖼️';
    } else if (extension === 'pdf') {
        return '📄';
    } else if (['doc', 'docx'].includes(extension)) {
        return '📝';
    } else if (['xls', 'xlsx'].includes(extension)) {
        return '📊';
    } else if (['ppt', 'pptx'].includes(extension)) {
        return '📽️';
    } else if (['txt', 'md'].includes(extension)) {
        return '📄';
    } else {
        return '📁';
    }
};

const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
};

const getStatusBadgeClass = (status: string) => {
    switch (status) {
        case 'completed':
        case 'uploaded':
            return 'bg-success/10 text-success-foreground border-success';
        case 'processing':
            return 'bg-warning/10 text-warning-foreground border-warning';
        case 'failed':
        case 'error':
            return 'bg-destructive/10 text-destructive-foreground border-destructive';
        default:
            return 'bg-muted text-muted-foreground border-border';
    }
};

export const FileGrid: React.FC<FileGridProps> = ({
    files,
    selectedFiles,
    onSelectionChange,
    onPreview,
    onDownload,
    onShare,
    onDelete,
    loading = false,
}) => {
    if (loading) {
        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 p-4">
                {Array.from({ length: 12 }).map((_, index) => (
                    <div key={index} className="bg-background border border-border rounded-lg p-4 animate-pulse">
                        <div className="w-12 h-12 bg-muted rounded-lg mb-3 mx-auto" />
                        <div className="h-4 bg-muted rounded mb-2" />
                        <div className="h-3 bg-muted rounded w-16 mx-auto" />
                    </div>
                ))}
            </div>
        );
    }

    if (files.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <FileText className="h-12 w-12 mb-4 text-muted" />
                <p className="text-lg font-medium mb-2">No files found</p>
                <p className="text-sm">Try adjusting your search or filters</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 p-4">
            {files.map((file) => {
                const isSelected = selectedFiles.includes(file.filename);

                return (
                    <div
                        key={file.filename}
                        className={cn(
                            'relative bg-background border border-border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer group',
                            isSelected && 'ring-2 ring-info border-info'
                        )}
                        onClick={() => onPreview(file)}
                    >
                        {/* Selection checkbox */}
                        <div className="absolute top-2 left-2 z-10">
                            <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={(e) => {
                                    e.stopPropagation();
                                    onSelectionChange(file.filename, e.target.checked);
                                }}
                                className="rounded border-border text-info focus:ring-info"
                                aria-label={`Select ${file.filename}`}
                            />
                        </div>

                        {/* Actions menu */}
                        <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0 bg-background shadow-sm border border-border"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    const menu = e.currentTarget.nextElementSibling as HTMLElement;
                                    if (menu) {
                                        menu.classList.toggle('hidden');
                                    }
                                }}
                            >
                                <MoreVertical className="h-4 w-4" />
                                <span className="sr-only">Open menu</span>
                            </Button>
                            <div className="hidden absolute right-0 mt-2 w-48 bg-background rounded-md shadow-lg border border-border z-20">
                                <div className="py-1">
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onPreview(file);
                                        }}
                                    >
                                        <Eye className="mr-2 h-4 w-4" />
                                        Preview
                                    </button>
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onDownload(file);
                                        }}
                                    >
                                        <Download className="mr-2 h-4 w-4" />
                                        Download
                                    </button>
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onShare(file);
                                        }}
                                    >
                                        <Share2 className="mr-2 h-4 w-4" />
                                        Share
                                    </button>
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-destructive hover:bg-muted"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onDelete(file);
                                        }}
                                    >
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* File icon */}
                        <div className="flex justify-center mb-3">
                            <div className="text-3xl">
                                {getFileIcon(file.filename)}
                            </div>
                        </div>

                        {/* File name */}
                        <h3 className="text-sm font-medium text-foreground text-center mb-2 truncate" title={file.filename}>
                            {file.filename}
                        </h3>

                        {/* File details */}
                        <div className="space-y-1 text-xs text-muted-foreground text-center">
                            <div>{formatFileSize(getFileSize(file))}</div>
                            <div>{formatDate(file.createdAt)}</div>
                            <div>
                                <span className={cn(
                                    'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
                                    getStatusBadgeClass(file.status || 'unknown')
                                )}>
                                    {file.status || 'Unknown'}
                                </span>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
