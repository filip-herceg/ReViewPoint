import React, { useState } from 'react';
import { X, Filter, Calendar, FileType, User, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

export interface FileFilters {
    status: string[];
    contentType: string[];
    sizeRange: { min: number; max: number } | null;
    dateRange: { start: string; end: string } | null;
    userId: number | null;
}

interface FileSearchFiltersProps {
    isOpen: boolean;
    onClose: () => void;
    filters: FileFilters;
    onFiltersChange: (filters: FileFilters) => void;
    onClearFilters: () => void;
    totalFiles: number;
    filteredFiles: number;
}

const STATUS_OPTIONS = [
    { value: 'completed', label: 'Completed', color: 'text-green-600' },
    { value: 'processing', label: 'Processing', color: 'text-yellow-600' },
    { value: 'failed', label: 'Failed', color: 'text-red-600' },
    { value: 'pending', label: 'Pending', color: 'text-gray-600' },
];

const CONTENT_TYPE_OPTIONS = [
    { value: 'application/pdf', label: 'PDF Documents' },
    { value: 'image/', label: 'Images' },
    { value: 'text/', label: 'Text Files' },
    { value: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', label: 'Word Documents' },
    { value: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', label: 'Excel Spreadsheets' },
    { value: 'application/vnd.openxmlformats-officedocument.presentationml.presentation', label: 'PowerPoint' },
];

const SIZE_PRESETS = [
    { label: 'Small (< 1MB)', min: 0, max: 1024 * 1024 },
    { label: 'Medium (1-10MB)', min: 1024 * 1024, max: 10 * 1024 * 1024 },
    { label: 'Large (10-100MB)', min: 10 * 1024 * 1024, max: 100 * 1024 * 1024 },
    { label: 'Very Large (> 100MB)', min: 100 * 1024 * 1024, max: Infinity },
];

export const FileSearchFilters: React.FC<FileSearchFiltersProps> = ({
    isOpen,
    onClose,
    filters,
    onFiltersChange,
    onClearFilters,
    totalFiles,
    filteredFiles,
}) => {
    const [tempFilters, setTempFilters] = useState<FileFilters>(filters);

    if (!isOpen) return null;

    const handleStatusToggle = (status: string) => {
        const newStatus = tempFilters.status.includes(status)
            ? tempFilters.status.filter(s => s !== status)
            : [...tempFilters.status, status];

        setTempFilters({ ...tempFilters, status: newStatus });
    };

    const handleContentTypeToggle = (contentType: string) => {
        const newContentType = tempFilters.contentType.includes(contentType)
            ? tempFilters.contentType.filter(ct => ct !== contentType)
            : [...tempFilters.contentType, contentType];

        setTempFilters({ ...tempFilters, contentType: newContentType });
    };

    const handleSizePresetSelect = (min: number, max: number) => {
        setTempFilters({
            ...tempFilters,
            sizeRange: max === Infinity ? { min, max: Number.MAX_SAFE_INTEGER } : { min, max }
        });
    };

    const handleDateRangeChange = (field: 'start' | 'end', value: string) => {
        const currentRange = tempFilters.dateRange || { start: '', end: '' };
        setTempFilters({
            ...tempFilters,
            dateRange: { ...currentRange, [field]: value }
        });
    };

    const applyFilters = () => {
        onFiltersChange(tempFilters);
        onClose();
    };

    const clearFilters = () => {
        const emptyFilters: FileFilters = {
            status: [],
            contentType: [],
            sizeRange: null,
            dateRange: null,
            userId: null,
        };
        setTempFilters(emptyFilters);
        onClearFilters();
    };

    const hasActiveFilters = tempFilters.status.length > 0 ||
        tempFilters.contentType.length > 0 ||
        tempFilters.sizeRange !== null ||
        tempFilters.dateRange !== null ||
        tempFilters.userId !== null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div
                className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
                role="dialog"
                aria-modal="true"
                aria-labelledby="filter-modal-title"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b">
                    <div className="flex items-center space-x-3">
                        <Filter className="h-5 w-5 text-gray-600" />
                        <h2 id="filter-modal-title" className="text-lg font-semibold text-gray-900">Filter Files</h2>
                    </div>
                    <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-600">
                            {filteredFiles} of {totalFiles} files
                        </span>
                        <Button variant="ghost" size="sm" onClick={onClose}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                        {/* Status Filter */}
                        <div className="space-y-3">
                            <h3 className="text-sm font-medium text-gray-900 flex items-center">
                                <Tag className="h-4 w-4 mr-2" />
                                Status
                            </h3>
                            <div className="space-y-2">
                                {STATUS_OPTIONS.map((option) => (
                                    <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={tempFilters.status.includes(option.value)}
                                            onChange={() => handleStatusToggle(option.value)}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className={cn('text-sm', option.color)}>{option.label}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* File Type Filter */}
                        <div className="space-y-3">
                            <h3 className="text-sm font-medium text-gray-900 flex items-center">
                                <FileType className="h-4 w-4 mr-2" />
                                File Type
                            </h3>
                            <div className="space-y-2">
                                {CONTENT_TYPE_OPTIONS.map((option) => (
                                    <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={tempFilters.contentType.includes(option.value)}
                                            onChange={() => handleContentTypeToggle(option.value)}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-sm text-gray-700">{option.label}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Size Filter */}
                        <div className="space-y-3">
                            <h3 className="text-sm font-medium text-gray-900">File Size</h3>
                            <div className="space-y-2">
                                {SIZE_PRESETS.map((preset, index) => (
                                    <label key={index} className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="sizePreset"
                                            checked={tempFilters.sizeRange?.min === preset.min &&
                                                (preset.max === Infinity ?
                                                    tempFilters.sizeRange?.max === Number.MAX_SAFE_INTEGER :
                                                    tempFilters.sizeRange?.max === preset.max)}
                                            onChange={() => handleSizePresetSelect(preset.min, preset.max)}
                                            className="text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-sm text-gray-700">{preset.label}</span>
                                    </label>
                                ))}
                                <label className="flex items-center space-x-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="sizePreset"
                                        checked={tempFilters.sizeRange === null}
                                        onChange={() => setTempFilters({ ...tempFilters, sizeRange: null })}
                                        className="text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-gray-700">Any size</span>
                                </label>
                            </div>
                        </div>

                        {/* Date Range Filter */}
                        <div className="space-y-3">
                            <h3 className="text-sm font-medium text-gray-900 flex items-center">
                                <Calendar className="h-4 w-4 mr-2" />
                                Upload Date
                            </h3>
                            <div className="space-y-2">
                                <div>
                                    <label className="text-xs text-gray-600">From</label>
                                    <Input
                                        type="date"
                                        value={tempFilters.dateRange?.start || ''}
                                        onChange={(e) => handleDateRangeChange('start', e.target.value)}
                                        className="mt-1"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-gray-600">To</label>
                                    <Input
                                        type="date"
                                        value={tempFilters.dateRange?.end || ''}
                                        onChange={(e) => handleDateRangeChange('end', e.target.value)}
                                        className="mt-1"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* User Filter */}
                        <div className="space-y-3 md:col-span-2">
                            <h3 className="text-sm font-medium text-gray-900 flex items-center">
                                <User className="h-4 w-4 mr-2" />
                                Uploaded By
                            </h3>
                            <Input
                                type="number"
                                placeholder="Enter user ID"
                                value={tempFilters.userId || ''}
                                onChange={(e) => setTempFilters({
                                    ...tempFilters,
                                    userId: e.target.value ? parseInt(e.target.value) : null
                                })}
                            />
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t bg-gray-50">
                    <Button
                        variant="outline"
                        onClick={clearFilters}
                        disabled={!hasActiveFilters}
                    >
                        Clear All Filters
                    </Button>
                    <div className="flex space-x-3">
                        <Button variant="outline" onClick={onClose}>
                            Cancel
                        </Button>
                        <Button onClick={applyFilters}>
                            Apply Filters
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};
