import React from 'react';
import { Download, Share2, Trash2, X, Archive, FolderPlus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FileBulkActionsProps {
    selectedCount: number;
    onDownloadSelected: () => void;
    onShareSelected: () => void;
    onDeleteSelected: () => void;
    onArchiveSelected: () => void;
    onMoveSelected: () => void;
    onClearSelection: () => void;
    isVisible: boolean;
    isLoading?: boolean;
}

export const FileBulkActions: React.FC<FileBulkActionsProps> = ({
    selectedCount,
    onDownloadSelected,
    onShareSelected,
    onDeleteSelected,
    onArchiveSelected,
    onMoveSelected,
    onClearSelection,
    isVisible,
    isLoading = false,
}) => {
    if (!isVisible || selectedCount === 0) {
        return null;
    }

    return (
        <div className={cn(
            'fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-50 transition-transform duration-300',
            isVisible ? 'translate-y-0' : 'translate-y-full'
        )}>
            <div className="max-w-7xl mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    {/* Left section - Selection info and clear */}
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-900">
                                {selectedCount} file{selectedCount !== 1 ? 's' : ''} selected
                            </span>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={onClearSelection}
                                className="h-6 w-6 p-0"
                                disabled={isLoading}
                            >
                                <X className="h-4 w-4" />
                                <span className="sr-only">Clear selection</span>
                            </Button>
                        </div>
                    </div>

                    {/* Center section - Bulk actions */}
                    <div className="flex items-center space-x-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onDownloadSelected}
                            disabled={isLoading}
                            className="whitespace-nowrap"
                        >
                            <Download className="h-4 w-4 mr-2" />
                            Download ({selectedCount})
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onShareSelected}
                            disabled={isLoading}
                            className="whitespace-nowrap"
                        >
                            <Share2 className="h-4 w-4 mr-2" />
                            Share
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onMoveSelected}
                            disabled={isLoading}
                            className="whitespace-nowrap"
                        >
                            <FolderPlus className="h-4 w-4 mr-2" />
                            Move
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onArchiveSelected}
                            disabled={isLoading}
                            className="whitespace-nowrap"
                        >
                            <Archive className="h-4 w-4 mr-2" />
                            Archive
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onDeleteSelected}
                            disabled={isLoading}
                            className="whitespace-nowrap text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                        >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                        </Button>
                    </div>

                    {/* Right section - More actions dropdown */}
                    <div className="relative">
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={isLoading}
                            onClick={(e) => {
                                e.preventDefault();
                                const menu = e.currentTarget.nextElementSibling as HTMLElement;
                                if (menu) {
                                    menu.classList.toggle('hidden');
                                }
                            }}
                        >
                            More actions
                        </Button>
                        <div className="hidden absolute bottom-full right-0 mb-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                            <div className="py-1">
                                <button
                                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    onClick={() => {
                                        // Add to favorites functionality
                                        console.log('Add to favorites');
                                    }}
                                >
                                    <span className="mr-2">⭐</span>
                                    Add to Favorites
                                </button>
                                <button
                                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    onClick={() => {
                                        // Copy links functionality
                                        console.log('Copy links');
                                    }}
                                >
                                    <span className="mr-2">🔗</span>
                                    Copy Links
                                </button>
                                <button
                                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    onClick={() => {
                                        // Export metadata functionality
                                        console.log('Export metadata');
                                    }}
                                >
                                    <span className="mr-2">📋</span>
                                    Export Metadata
                                </button>
                                <div className="border-t border-gray-100 my-1" />
                                <button
                                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    onClick={() => {
                                        // Change permissions functionality
                                        console.log('Change permissions');
                                    }}
                                >
                                    <span className="mr-2">🔒</span>
                                    Change Permissions
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Loading indicator */}
                {isLoading && (
                    <div className="mt-3 flex items-center justify-center">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            <span>Processing selected files...</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
