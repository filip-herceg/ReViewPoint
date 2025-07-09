import React from 'react';
import { FileText, Download, Share2, Trash2, Eye, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { formatFileSize as formatFileSizeUtil, getFileTypeGroup } from '@/lib/utils/fileUtils';
import type { FileItem } from '@/lib/store/fileManagementStore';

interface FileListProps {
    files: FileItem[];
    selectedFiles: string[];
    onSelectionChange: (fileId: string, selected: boolean) => void;
    onPreview: (file: FileItem) => void;
    onDownload: (file: FileItem) => void;
    onShare: (file: FileItem) => void;
    onDelete: (file: FileItem) => void;
    loading?: boolean;
}

// Get file size utility (placeholder since size is not in FileItem)
const getFileSize = (file: FileItem): number => {
    // Since the FileItem doesn't include size, we'll return 0
    // In a real implementation, this would come from the API
    return 0;
};

const formatDate = (dateString: string): string => {
    if (dateString === 'Unknown') return dateString;

    try {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    } catch {
        return 'Invalid date';
    }
};

const getStatusBadgeClass = (status: string) => {
    switch (status) {
        case 'completed':
        case 'uploaded':
            return 'bg-green-100 text-green-800 border-green-200';
        case 'processing':
            return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        case 'failed':
        case 'error':
            return 'bg-red-100 text-red-800 border-red-200';
        default:
            return 'bg-gray-100 text-gray-800 border-gray-200';
    }
};

export const FileList: React.FC<FileListProps> = ({
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
            <div className="space-y-2 p-4">
                {Array.from({ length: 8 }).map((_, index) => (
                    <div key={index} className="flex items-center space-x-4 p-3 bg-white border rounded-lg animate-pulse">
                        <div className="h-4 w-4 bg-gray-200 rounded" />
                        <div className="h-5 w-5 bg-gray-200 rounded" />
                        <div className="flex-1 space-y-2">
                            <div className="h-4 bg-gray-200 rounded w-1/3" />
                            <div className="h-3 bg-gray-200 rounded w-1/2" />
                        </div>
                        <div className="h-6 w-16 bg-gray-200 rounded-full" />
                        <div className="h-8 w-8 bg-gray-200 rounded" />
                    </div>
                ))}
            </div>
        );
    }

    if (files.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <FileText className="h-12 w-12 mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">No files found</p>
                <p className="text-sm">Try adjusting your search or filters</p>
            </div>
        );
    }

    return (
        <div className="space-y-2 p-4">
            {files.map((file) => {
                const isSelected = selectedFiles.includes(file.filename);

                return (
                    <div
                        key={file.filename}
                        className={cn(
                            'flex items-center space-x-4 p-3 bg-white border rounded-lg hover:shadow-sm transition-shadow cursor-pointer group',
                            isSelected && 'ring-2 ring-blue-500 border-blue-300'
                        )}
                        onClick={() => onPreview(file)}
                    >
                        {/* Selection checkbox */}
                        <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => {
                                e.stopPropagation();
                                onSelectionChange(file.filename, e.target.checked);
                            }}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            aria-label={`Select ${file.filename}`}
                        />

                        {/* File icon */}
                        <div className="flex-shrink-0">
                            <FileText className="h-5 w-5 text-gray-400" />
                        </div>

                        {/* File details */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-medium text-gray-900 truncate" title={file.filename}>
                                    {file.filename}
                                </h3>
                                <div className="ml-4 text-xs text-gray-500">
                                    {formatFileSizeUtil(getFileSize(file))}
                                </div>
                            </div>
                            <div className="flex items-center justify-between mt-1">
                                <p className="text-xs text-gray-500">
                                    {getFileTypeGroup(file.filename).toUpperCase()} • {formatDate(file.createdAt || 'Unknown')}
                                </p>
                            </div>
                        </div>

                        {/* Status badge */}
                        <div className="flex-shrink-0">
                            <span className={cn(
                                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
                                getStatusBadgeClass(file.status || 'unknown')
                            )}>
                                {file.status || 'Unknown'}
                            </span>
                        </div>

                        {/* Actions menu */}
                        <div className="flex-shrink-0 relative opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0"
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
                            <div className="hidden absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                                <div className="py-1">
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onPreview(file);
                                        }}
                                    >
                                        <Eye className="mr-2 h-4 w-4" />
                                        Preview
                                    </button>
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onDownload(file);
                                        }}
                                    >
                                        <Download className="mr-2 h-4 w-4" />
                                        Download
                                    </button>
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onShare(file);
                                        }}
                                    >
                                        <Share2 className="mr-2 h-4 w-4" />
                                        Share
                                    </button>
                                    <button
                                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
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
                    </div>
                );
            })}
        </div>
    );
};
