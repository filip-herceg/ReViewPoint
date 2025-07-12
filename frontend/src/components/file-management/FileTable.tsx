import React from "react";
import {
  FileText,
  Download,
  Share2,
  Trash2,
  Eye,
  MoreVertical,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Define FileItem type to match the store
import type { FileItem as StoreFileItem } from "@/lib/store/fileManagementStore";
type FileItem = StoreFileItem;

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
    case "completed":
      return "bg-success/10 text-success-foreground border-success";
    case "processing":
      return "bg-warning/10 text-warning-foreground border-warning";
    case "failed":
      return "bg-destructive/10 text-destructive-foreground border-destructive";
    default:
      return "bg-muted text-muted-foreground border-border";
  }
};

const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return "Unknown";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const getFileType = (filename: string): string => {
  const extension = filename.split(".").pop()?.toLowerCase() || "";
  switch (extension) {
    case "pdf":
      return "PDF";
    case "jpg":
    case "jpeg":
    case "png":
    case "gif":
    case "webp":
      return "Image";
    case "txt":
    case "md":
      return "Text";
    case "doc":
    case "docx":
      return "Word";
    case "xls":
    case "xlsx":
      return "Excel";
    case "ppt":
    case "pptx":
      return "PowerPoint";
    default:
      return extension.toUpperCase() || "File";
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
  const allSelected =
    files.length > 0 &&
    files.every((file) => selectedFiles.includes(file.filename));
  const someSelected = selectedFiles.length > 0 && !allSelected;

  return (
    <div className="rounded-md border border-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted border-b border-border">
            <tr>
              <th className="w-12 px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el: HTMLInputElement | null) => {
                    if (el) el.indeterminate = someSelected;
                  }}
                  onChange={(e) => onSelectAll(e.target.checked)}
                  className="rounded border-border text-info focus:ring-info"
                  aria-label="Select all files"
                />
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-foreground">
                Name
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-foreground">
                Type
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-foreground">
                Size
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-foreground">
                Status
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-foreground">
                Uploaded
              </th>
              <th className="w-16 px-4 py-3 text-left text-sm font-medium text-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-background divide-y divide-border">
            {loading ? (
              Array.from({ length: 5 }).map((_, index) => (
                <tr key={index}>
                  <td colSpan={7} className="px-4 py-4">
                    <div className="flex items-center space-x-4">
                      <div className="h-4 w-4 bg-muted rounded animate-pulse" />
                      <div className="h-4 w-32 bg-muted rounded animate-pulse" />
                      <div className="h-4 w-16 bg-muted rounded animate-pulse" />
                      <div className="h-4 w-20 bg-muted rounded animate-pulse" />
                      <div className="h-4 w-24 bg-muted rounded animate-pulse" />
                      <div className="h-4 w-32 bg-muted rounded animate-pulse" />
                    </div>
                  </td>
                </tr>
              ))
            ) : files.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="px-4 py-8 text-center text-muted-foreground"
                >
                  No files found
                </td>
              </tr>
            ) : (
              files.map((file) => (
                <tr key={file.filename} className="hover:bg-muted">
                  <td className="px-4 py-4">
                    <input
                      type="checkbox"
                      checked={selectedFiles.includes(file.filename)}
                      onChange={(e) =>
                        onSelectionChange(file.filename, e.target.checked)
                      }
                      className="rounded border-border text-info focus:ring-info"
                      aria-label={`Select ${file.filename}`}
                    />
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4 text-muted" />
                      <span
                        className="font-medium text-foreground truncate max-w-xs"
                        title={file.filename}
                      >
                        {file.filename}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-muted-foreground uppercase">
                      {getFileType(file.filename)}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-foreground">
                      {/* Size not available in current FileItem interface */}
                      N/A
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span
                      className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
                        getStatusBadgeClass(file.status || "unknown"),
                      )}
                    >
                      {file.status || "Unknown"}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-muted-foreground">
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
                          const menu = e.currentTarget
                            .nextElementSibling as HTMLElement;
                          if (menu) {
                            menu.classList.toggle("hidden");
                          }
                        }}
                      >
                        <MoreVertical className="h-4 w-4" />
                        <span className="sr-only">Open menu</span>
                      </Button>
                      <div className="hidden absolute right-0 mt-2 w-48 bg-background rounded-md shadow-lg border border-border z-10">
                        <div className="py-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted justify-start"
                            onClick={() => onPreview(file)}
                          >
                            <Eye className="mr-2 h-4 w-4" />
                            Preview
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted justify-start"
                            onClick={() => onDownload(file)}
                          >
                            <Download className="mr-2 h-4 w-4" />
                            Download
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted justify-start"
                            onClick={() => onShare(file)}
                          >
                            <Share2 className="mr-2 h-4 w-4" />
                            Share
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="flex items-center w-full px-4 py-2 text-sm text-destructive hover:bg-muted justify-start"
                            onClick={() => onDelete(file)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </Button>
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
