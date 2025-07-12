import React, { useState, useEffect } from "react";
import {
  X,
  Download,
  Share2,
  Trash2,
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  formatFileSize as formatFileSizeUtil,
  getFileTypeGroup,
} from "@/lib/utils/fileUtils";
import type { FileItem } from "@/lib/store/fileManagementStore";

interface FilePreviewModalProps {
  file: FileItem | null;
  isOpen: boolean;
  onClose: () => void;
  onDownload: (file: FileItem) => void;
  onShare: (file: FileItem) => void;
  onDelete: (file: FileItem) => void;
  onPrevious?: () => void;
  onNext?: () => void;
  hasPrevious?: boolean;
  hasNext?: boolean;
}

// Get file size utility (placeholder since size is not in FileItem)
const getFileSize = (file: FileItem): number => {
  // Since the FileItem doesn't include size, we'll return 0
  // In a real implementation, this would come from the API
  return 0;
};

// Get content type from filename
const getContentType = (filename: string): string => {
  const extension = filename.split(".").pop()?.toLowerCase() || "";
  const mimeTypes: Record<string, string> = {
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    png: "image/png",
    gif: "image/gif",
    pdf: "application/pdf",
    txt: "text/plain",
    doc: "application/msword",
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  };
  return mimeTypes[extension] || "application/octet-stream";
};

const formatDate = (dateString?: string): string => {
  if (!dateString) return "Unknown";

  try {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "Invalid date";
  }
};

const getFileUrl = (filename: string): string => {
  // This would normally come from your API
  return `/api/files/${encodeURIComponent(filename)}`;
};

export const FilePreviewModal: React.FC<FilePreviewModalProps> = ({
  file,
  isOpen,
  onClose,
  onDownload,
  onShare,
  onDelete,
  onPrevious,
  onNext,
  hasPrevious = false,
  hasNext = false,
}) => {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (file) {
      setZoom(100);
      setRotation(0);
      setIsLoading(true);
      setError(null);
    }
  }, [file]);

  if (!isOpen || !file) return null;

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 25));
  const handleRotate = () => setRotation((prev) => (prev + 90) % 360);

  const canPreview = (contentType: string): boolean => {
    return (
      contentType.startsWith("image/") ||
      contentType === "application/pdf" ||
      contentType.startsWith("text/")
    );
  };

  const renderPreviewContent = () => {
    const contentType = getContentType(file.filename);
    const { filename } = file;
    const fileUrl = getFileUrl(filename);

    if (!canPreview(contentType)) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-lg font-medium mb-2">Preview not available</h3>
          <p className="text-sm text-center mb-4">
            This file type ({contentType}) cannot be previewed.
          </p>
          <Button onClick={() => onDownload(file)}>
            <Download className="h-4 w-4 mr-2" />
            Download to view
          </Button>
        </div>
      );
    }

    if (contentType.startsWith("image/")) {
      return (
        <div className="flex items-center justify-center h-full">
          <img
            src={fileUrl}
            alt={filename}
            className="max-w-full max-h-full object-contain transition-transform duration-200"
            style={{
              transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
            }}
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setIsLoading(false);
              setError("Failed to load image");
            }}
          />
        </div>
      );
    }

    if (contentType === "application/pdf") {
      return (
        <div className="w-full h-full">
          <iframe
            src={`${fileUrl}#toolbar=1&navpanes=1&scrollbar=1`}
            className="w-full h-full border-0"
            title={`Preview of ${filename}`}
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setIsLoading(false);
              setError("Failed to load PDF");
            }}
          />
        </div>
      );
    }

    if (contentType.startsWith("text/")) {
      return (
        <div className="w-full h-full p-4 overflow-auto">
          <iframe
            src={fileUrl}
            className="w-full h-full border-0 bg-white"
            title={`Preview of ${filename}`}
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setIsLoading(false);
              setError("Failed to load text file");
            }}
          />
        </div>
      );
    }

    return null;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center">
      {/* Modal container */}
      <div
        role="dialog"
        aria-labelledby="preview-title"
        aria-modal="true"
        className="relative w-full h-full max-w-6xl max-h-screen m-4 bg-background rounded-lg shadow-xl overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-muted">
          <div className="flex items-center space-x-4 min-w-0 flex-1">
            <h2
              id="preview-title"
              className="text-lg font-semibold text-foreground truncate"
              title={file.filename}
            >
              {file.filename}
            </h2>
            <div className="text-sm text-muted-foreground">
              {formatFileSizeUtil(getFileSize(file))} •{" "}
              {formatDate(file.createdAt)}
            </div>
          </div>

          {/* Navigation and action buttons */}
          <div className="flex items-center space-x-2">
            {/* Navigation */}
            {(hasPrevious || hasNext) && (
              <div className="flex items-center space-x-1 mr-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onPrevious}
                  disabled={!hasPrevious}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onNext}
                  disabled={!hasNext}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}

            {/* Zoom controls for images */}
            {getContentType(file.filename).startsWith("image/") && (
              <div className="flex items-center space-x-1 mr-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleZoomOut}
                  disabled={zoom <= 25}
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <span className="text-xs text-muted-foreground w-12 text-center">
                  {zoom}%
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleZoomIn}
                  disabled={zoom >= 200}
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" onClick={handleRotate}>
                  <RotateCw className="h-4 w-4" />
                </Button>
              </div>
            )}

            {/* Action buttons */}
            <Button variant="ghost" size="sm" onClick={() => onDownload(file)}>
              <Download className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => onShare(file)}>
              <Share2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(file)}
              className="text-destructive hover:text-destructive-foreground"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 relative overflow-hidden bg-muted">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex flex-col items-center space-y-2">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-info" />
                <span className="text-sm text-muted-foreground">
                  Loading preview...
                </span>
              </div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex flex-col items-center space-y-2 text-destructive">
                <span className="text-lg">⚠️</span>
                <span className="text-sm">{error}</span>
                <Button variant="outline" onClick={() => onDownload(file)}>
                  <Download className="h-4 w-4 mr-2" />
                  Download file
                </Button>
              </div>
            </div>
          )}

          {!isLoading && !error && renderPreviewContent()}
        </div>

        {/* Footer with file details */}
        <div className="p-4 border-t border-border bg-muted">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium text-muted-foreground">Type:</span>
              <span className="ml-2 text-foreground">
                {getContentType(file.filename)}
              </span>
            </div>
            <div>
              <span className="font-medium text-muted-foreground">Size:</span>
              <span className="ml-2 text-foreground">
                {formatFileSizeUtil(getFileSize(file))}
              </span>
            </div>
            <div>
              <span className="font-medium text-muted-foreground">Status:</span>
              <span
                className={cn(
                  "ml-2 px-2 py-0.5 rounded-full text-xs font-medium",
                  file.status === "uploaded" &&
                    "bg-success/10 text-success-foreground",
                  file.status === "processing" &&
                    "bg-warning/10 text-warning-foreground",
                  file.status === "error" &&
                    "bg-destructive/10 text-destructive-foreground",
                )}
              >
                {file.status}
              </span>
            </div>
            <div>
              <span className="font-medium text-muted-foreground">
                Uploaded:
              </span>
              <span className="ml-2 text-foreground">
                {formatDate(file.createdAt)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
