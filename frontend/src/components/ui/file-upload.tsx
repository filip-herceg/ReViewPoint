/**
 * FileUpload Component - Drag & drop file upload with progress and validation
 * Part of Phase 2.4 UI Design System
 */

import type React from "react";
import { useCallback, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import logger from "@/logger";

// File validation rules
export interface FileValidation {
  maxSize?: number; // bytes
  maxFiles?: number;
  allowedTypes?: string[]; // MIME types or extensions
  minFiles?: number;
}

// Upload file info
export interface UploadFile {
  id: string;
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  progress: number;
  error?: string;
  url?: string; // Result URL after upload
}

// FileUpload props
export interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  onUpload?: (files: UploadFile[]) => Promise<void>;
  validation?: FileValidation;
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
  dropzoneText?: string;
  browseText?: string;
  uploadText?: string;
  showPreview?: boolean;
  autoUpload?: boolean;
  testId?: string;
}

// Default validation
const DEFAULT_VALIDATION: FileValidation = {
  maxSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 10,
  allowedTypes: ["*"],
  minFiles: 0,
};

// Generate unique ID
const generateId = (): string => {
  return `file-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
};

// Format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`;
};

// Validate file
const validateFile = (
  file: File,
  validation: FileValidation,
): string | null => {
  // Check file size
  if (validation.maxSize && file.size > validation.maxSize) {
    return `File size exceeds ${formatFileSize(validation.maxSize)}`;
  }

  // Check file type
  if (
    validation.allowedTypes &&
    validation.allowedTypes.length > 0 &&
    !validation.allowedTypes.includes("*")
  ) {
    const fileType = file.type;
    const fileName = file.name.toLowerCase();
    const isTypeAllowed = validation.allowedTypes.some((type) => {
      if (type.startsWith(".")) {
        return fileName.endsWith(type.toLowerCase());
      }
      return fileType === type || fileType.startsWith(`${type.split("/")[0]}/`);
    });

    if (!isTypeAllowed) {
      return `File type not allowed. Allowed types: ${validation.allowedTypes.join(", ")}`;
    }
  }

  return null;
};

/**
 * Comprehensive file upload component with drag & drop, validation, and progress
 */
export function FileUpload({
  onFilesSelected,
  onUpload,
  validation = DEFAULT_VALIDATION,
  multiple = false,
  disabled = false,
  className,
  dropzoneText = "Drag & drop files here, or click to browse",
  browseText = "Browse Files",
  uploadText = "Upload Files",
  showPreview = true,
  autoUpload = false,
  testId = "file-upload",
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [_dragCounter, setDragCounter] = useState(0);

  const mergedValidation = useMemo(
    () => ({ ...DEFAULT_VALIDATION, ...validation }),
    [validation],
  );

  // Handle upload
  const handleUpload = useCallback(
    async (filesToUpload = files) => {
      if (!onUpload || filesToUpload.length === 0) return;

      try {
        // Update status to uploading
        setFiles((prev) =>
          prev.map((f) =>
            filesToUpload.find((upload) => upload.id === f.id)
              ? { ...f, status: "uploading" as const, progress: 0 }
              : f,
          ),
        );

        logger.info("Starting file upload", { count: filesToUpload.length });
        await onUpload(filesToUpload);

        // Update status to success (onUpload should handle progress updates)
        setFiles((prev) =>
          prev.map((f) =>
            filesToUpload.find((upload) => upload.id === f.id)
              ? { ...f, status: "success" as const, progress: 100 }
              : f,
          ),
        );

        logger.info("File upload completed", { count: filesToUpload.length });
      } catch (err) {
        logger.error("File upload failed", { error: err });

        // Update status to error
        setFiles((prev) =>
          prev.map((f) =>
            filesToUpload.find((upload) => upload.id === f.id)
              ? {
                  ...f,
                  status: "error" as const,
                  error: err instanceof Error ? err.message : "Upload failed",
                }
              : f,
          ),
        );
      }
    },
    [files, onUpload],
  );

  // Handle file selection
  const handleFiles = useCallback(
    (selectedFiles: FileList | File[]) => {
      try {
        const fileArray = Array.from(selectedFiles);

        // Validate file count
        const totalFiles = files.length + fileArray.length;
        if (
          mergedValidation.maxFiles &&
          totalFiles > mergedValidation.maxFiles
        ) {
          logger.warn("Too many files selected", {
            selected: fileArray.length,
            existing: files.length,
            max: mergedValidation.maxFiles,
          });
          return;
        }

        // Validate and process files
        const validFiles: UploadFile[] = [];
        const errors: string[] = [];

        fileArray.forEach((file) => {
          const validationError = validateFile(file, mergedValidation);
          if (validationError) {
            errors.push(`${file.name}: ${validationError}`);
          } else {
            validFiles.push({
              id: generateId(),
              file,
              status: "pending",
              progress: 0,
            });
          }
        });

        if (errors.length > 0) {
          logger.error("File validation errors", { errors });
          // You might want to show these errors in a toast notification
          return;
        }

        // Update files state
        const newFiles = multiple ? [...files, ...validFiles] : validFiles;
        setFiles(newFiles);

        // Notify parent
        onFilesSelected(validFiles.map((f) => f.file));

        // Auto upload if enabled
        if (autoUpload && onUpload) {
          handleUpload(newFiles);
        }

        logger.info("Files selected", {
          count: validFiles.length,
          totalSize: validFiles.reduce((sum, f) => sum + f.file.size, 0),
        });
      } catch (err) {
        logger.error("Failed to handle file selection", { error: err });
      }
    },
    [
      files,
      mergedValidation,
      multiple,
      onFilesSelected,
      autoUpload,
      onUpload,
      handleUpload,
    ],
  );

  // Remove file
  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
    logger.debug("File removed", { fileId });
  }, []);

  // Drag handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter((prev) => prev + 1);
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter((prev) => {
      const newCounter = prev - 1;
      if (newCounter === 0) {
        setIsDragging(false);
      }
      return newCounter;
    });
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      setDragCounter(0);

      if (disabled) return;

      const { files: droppedFiles } = e.dataTransfer;
      if (droppedFiles && droppedFiles.length > 0) {
        handleFiles(droppedFiles);
      }
    },
    [disabled, handleFiles],
  );

  // File input change
  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const { files: selectedFiles } = e.target;
      if (selectedFiles && selectedFiles.length > 0) {
        handleFiles(selectedFiles);
      }
      // Reset input value to allow selecting the same file again
      e.target.value = "";
    },
    [handleFiles],
  );

  // Calculate upload statistics
  const pendingFiles = files.filter((f) => f.status === "pending");
  const uploadingFiles = files.filter((f) => f.status === "uploading");
  const successFiles = files.filter((f) => f.status === "success");
  const errorFiles = files.filter((f) => f.status === "error");
  const totalProgress =
    files.length > 0
      ? files.reduce((sum, f) => sum + f.progress, 0) / files.length
      : 0;

  return (
    <div className={cn("space-y-4", className)} data-testid={testId}>
      {/* Dropzone */}
      <Button
        type="button"
        variant="ghost"
        className={cn(
          // Use only semantic Tailwind color classes
          "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer w-full h-auto justify-center",
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50",
          disabled && "opacity-50 cursor-not-allowed",
          // Remove any hardcoded color values
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() =>
          !disabled && document.getElementById(`file-input-${testId}`)?.click()
        }
        disabled={disabled}
        aria-label="Click or drag to upload files"
        data-testid={`${testId}-dropzone`}
      >
        <input
          id={`file-input-${testId}`}
          type="file"
          multiple={multiple}
          disabled={disabled}
          className="hidden"
          onChange={handleFileInputChange}
          accept={mergedValidation.allowedTypes?.join(",") || undefined}
          data-testid={`${testId}-input`}
        />

        <div className="space-y-2">
          <div className="text-muted-foreground">{dropzoneText}</div>
          <Button
            type="button"
            variant="outline"
            disabled={disabled}
            data-testid={`${testId}-browse`}
          >
            {browseText}
          </Button>
        </div>

        {/* Validation info */}
        <div className="mt-4 text-xs text-muted-foreground space-y-1">
          {mergedValidation.maxSize && (
            <div>Max file size: {formatFileSize(mergedValidation.maxSize)}</div>
          )}
          {mergedValidation.allowedTypes &&
            mergedValidation.allowedTypes.length > 0 &&
            !mergedValidation.allowedTypes.includes("*") && (
              <div>
                Allowed types: {mergedValidation.allowedTypes.join(", ")}
              </div>
            )}
          {mergedValidation.maxFiles && multiple && (
            <div>Max files: {mergedValidation.maxFiles}</div>
          )}
        </div>
      </Button>

      {/* File list */}
      {showPreview && files.length > 0 && (
        <div className="space-y-2" data-testid={`${testId}-preview`}>
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-foreground">
              Selected Files ({files.length})
            </h4>
            {!autoUpload && onUpload && pendingFiles.length > 0 && (
              <Button
                onClick={() => handleUpload(pendingFiles)}
                disabled={disabled}
                data-testid={`${testId}-upload`}
              >
                {uploadText}
              </Button>
            )}
          </div>

          {/* Overall progress */}
          {(uploadingFiles.length > 0 || successFiles.length > 0) && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Overall Progress</span>
                <span>{Math.round(totalProgress)}%</span>
              </div>
              <Progress value={totalProgress} className="h-2" />
            </div>
          )}

          <div className="space-y-2">
            {files.map((uploadFile) => (
              <Card
                key={uploadFile.id}
                className="p-3 bg-card border border-card"
                data-testid={`${testId}-file-${uploadFile.id}`}
              >
                <CardContent className="p-0">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium truncate text-foreground">
                          {uploadFile.file.name}
                        </span>
                        <Badge
                          variant={
                            uploadFile.status === "success"
                              ? "default"
                              : uploadFile.status === "error"
                                ? "destructive"
                                : uploadFile.status === "uploading"
                                  ? "secondary"
                                  : "outline"
                          }
                        >
                          {uploadFile.status}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {formatFileSize(uploadFile.file.size)}
                      </div>
                      {uploadFile.error && (
                        <div className="text-sm text-destructive-foreground mt-1">
                          {uploadFile.error}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      {uploadFile.status === "uploading" && (
                        <div className="w-24">
                          <Progress
                            value={uploadFile.progress}
                            className="h-1"
                          />
                        </div>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(uploadFile.id)}
                        disabled={uploadFile.status === "uploading"}
                        data-testid={`${testId}-remove-${uploadFile.id}`}
                      >
                        ×
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Summary */}
          {files.length > 0 && (
            <div className="text-sm text-muted-foreground flex space-x-4">
              {pendingFiles.length > 0 && (
                <span>Pending: {pendingFiles.length}</span>
              )}
              {uploadingFiles.length > 0 && (
                <span>Uploading: {uploadingFiles.length}</span>
              )}
              {successFiles.length > 0 && (
                <span>Success: {successFiles.length}</span>
              )}
              {errorFiles.length > 0 && (
                <span>Errors: {errorFiles.length}</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
