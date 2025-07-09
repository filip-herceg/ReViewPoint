import React from 'react';
import { FileText, Download, Share2, Trash2, Eye, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Define FileItem type to match the store
interface FileItem {
    filename: string;
    url: string;
    status?: string;
    progress?: number;
    createdAt?: string;
}

interface FileTableProps {
    files: FileItem[];
    selectedFiles: string[];
    onSelectionChange: (fileId: string, selected: boolean) => void;
    onSelectAll: (selected: boolean) => void;
    onPreview: (file: FileItem) => void;
    onDownload: (file: FileItem) => void;
    onShare: (file: FileItem) => void;
    onDelete: (file: FileItem) => void;
    loading?: boolean;
}

const getStatusBadgeClass = (status: string) => {
    switch (status) {
        case 'completed':
            return 'bg-green-100 text-green-800 border-green-200';
        case 'processing':
            return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        case 'failed':
            return 'bg-red-100 text-red-800 border-red-200';
        default:
            return 'bg-gray-100 text-gray-800 border-gray-200';
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

const getFileType = (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase() || '';
    switch (extension) {
        case 'pdf': return 'PDF';
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
        case 'webp': return 'Image';
        case 'txt':
        case 'md': return 'Text';
        case 'doc':
        case 'docx': return 'Word';
        case 'xls':
        case 'xlsx': return 'Excel';
        case 'ppt':
        case 'pptx': return 'PowerPoint';
        default: return extension.toUpperCase() || 'File';
    }
};

export const FileTable: React.FC<FileTableProps> = ({
    files,
    selectedFiles,
    onSelectionChange,
    onSelectAll,
    onPreview,
    onDownload,
    onShare,
    onDelete,
    loading = false,
}) => {
    const allSelected = files.length > 0 && files.every(file => selectedFiles.includes(file.filename));
    const someSelected = selectedFiles.length > 0 && !allSelected;

    return (
        <div className="rounded-md border overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="w-12 px-4 py-3 text-left">
                                <input
                                    type="checkbox"
                                    checked={allSelected}
                                    ref={(el: HTMLInputElement | null) => {
                                        if (el) el.indeterminate = someSelected;
                                    }}
                                    onChange={(e) => onSelectAll(e.target.checked)}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    aria-label="Select all files"
                                />
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Name</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Type</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Size</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Status</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Uploaded</th>
                            <th className="w-16 px-4 py-3 text-left text-sm font-medium text-gray-900">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {loading ? (
                            Array.from({ length: 5 }).map((_, index) => (
                                <tr key={index}>
                                    <td colSpan={7} className="px-4 py-4">
                                        <div className="flex items-center space-x-4">
                                            <div className="h-4 w-4 bg-gray-200 rounded animate-pulse" />
                                            <div className="h-4 w-32 bg-gray-200 rounded animate-pulse" />
                                            <div className="h-4 w-16 bg-gray-200 rounded animate-pulse" />
                                            <div className="h-4 w-20 bg-gray-200 rounded animate-pulse" />
                                            <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                                            <div className="h-4 w-32 bg-gray-200 rounded animate-pulse" />
                                        </div>
                                    </td>
                                </tr>
                            ))
                        ) : files.length === 0 ? (
                            <tr>
                                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                                    No files found
                                </td>
                            </tr>
                        ) : (
                            files.map((file) => (
                                <tr key={file.filename} className="hover:bg-gray-50">
                                    <td className="px-4 py-4">
                                        <input
                                            type="checkbox"
                                            checked={selectedFiles.includes(file.filename)}
                                            onChange={(e) => onSelectionChange(file.filename, e.target.checked)}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                            aria-label={`Select ${file.filename}`}
                                        />
                                    </td>
                                    <td className="px-4 py-4">
                                        <div className="flex items-center space-x-2">
                                            <FileText className="h-4 w-4 text-gray-400" />
                                            <span className="font-medium text-gray-900 truncate max-w-xs" title={file.filename}>
                                                {file.filename}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-4">
                                        <span className="text-sm text-gray-500 uppercase">
                                            {getFileType(file.filename)}
                                        </span>
                                    </td>
                                    <td className="px-4 py-4">
                                        <span className="text-sm text-gray-900">
                                            {/* Size not available in current FileItem interface */}
                                            N/A
                                        </span>
                                    </td>
                                    <td className="px-4 py-4">
                                        <span className={cn(
                                            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
                                            getStatusBadgeClass(file.status || 'unknown')
                                        )}>
                                            {file.status || 'Unknown'}
                                        </span>
                                    </td>
                                    <td className="px-4 py-4">
                                        <span className="text-sm text-gray-500">
                                            {formatDate(file.createdAt)}
                                        </span>
                                    </td>
                                    <td className="px-4 py-4">
                                        <div className="relative">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-8 w-8 p-0"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    // Simple dropdown toggle - in a real app you'd use a proper dropdown
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
                                                        onClick={() => onPreview(file)}
                                                    >
                                                        <Eye className="mr-2 h-4 w-4" />
                                                        Preview
                                                    </button>
                                                    <button
                                                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                        onClick={() => onDownload(file)}
                                                    >
                                                        <Download className="mr-2 h-4 w-4" />
                                                        Download
                                                    </button>
                                                    <button
                                                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                        onClick={() => onShare(file)}
                                                    >
                                                        <Share2 className="mr-2 h-4 w-4" />
                                                        Share
                                                    </button>
                                                    <button
                                                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                                                        onClick={() => onDelete(file)}
                                                    >
                                                        <Trash2 className="mr-2 h-4 w-4" />
                                                        Delete
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
