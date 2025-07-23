// Upload and file management types
// Maps to backend/src/schemas/file.py and upload endpoints

import type { ISODateString, PaginatedResponse } from "./common";

/**
 * File metadata schema
 * Matches backend FileSchema
 */
export interface File {
  /** Unique identifier for the file */
  id: number;
  /** Name of the file */
  filename: string;
  /** MIME type of the file */
  content_type: string;
  /** ID of the user who owns the file */
  user_id: number;
  /** Timestamp when the file was created */
  created_at: ISODateString;
}

/**
 * File upload response
 * Matches backend FileUploadResponse
 */
export interface FileUploadResponse {
  /** Uploaded filename */
  filename: string;
  /** File access URL */
  url: string;
}

/**
 * File list item
 * Used in file listings
 */
export interface FileListItem {
  /** Filename */
  filename: string;
  /** File access URL (optional) */
  url?: string;
}

/**
 * File list response
 * Matches backend FileListResponse
 */
export interface FileListResponse {
  /** Array of files */
  files: FileListItem[];
  /** Total number of files */
  total: number;
}

/**
 * Paginated file list response
 */
export type PaginatedFileListResponse = PaginatedResponse<File>;

/**
 * Upload status types
 * Frontend-specific upload states
 */
export type UploadStatus =
  | "pending"
  | "uploading"
  | "completed"
  | "error"
  | "cancelled";

/**
 * Upload item (frontend representation)
 * Used by upload store and components
 */
export interface Upload {
  /** Unique upload ID (frontend generated) */
  id: string;
  /** Original filename */
  name: string;
  /** Upload status */
  status: UploadStatus;
  /** Upload progress percentage (0-100) */
  progress: number;
  /** Upload creation timestamp */
  createdAt: ISODateString;
  /** File size in bytes */
  size?: number;
  /** MIME type */
  type?: string;
  /** Server response on completion */
  response?: FileUploadResponse;
  /** Error message on failure */
  error?: string;
  /** Upload progress details */
  progressDetails?: UploadProgress;
}

/**
 * Upload creation request
 * Used when creating new uploads (excludes generated fields)
 */
export interface UploadCreateRequest {
  /** Unique upload ID (optional) */
  id?: string;
  /** Original filename */
  name: string;
  /** Upload status */
  status: UploadStatus;
  /** Upload progress percentage (0-100) */
  progress: number;
  /** Upload creation timestamp (optional) */
  createdAt?: ISODateString;
  /** File size in bytes */
  size?: number;
  /** MIME type */
  type?: string;
  /** Error message on failure */
  error?: string;
  /** Upload progress details */
  progressDetails?: UploadProgress;
}

/**
 * File upload request configuration
 */
export interface FileUploadConfig {
  /** Whether to allow multiple files */
  multiple?: boolean;
  /** Accepted file types (MIME types) */
  accept?: string[];
  /** Maximum file size in bytes */
  maxSize?: number;
  /** Maximum number of files */
  maxFiles?: number;
  /** Whether to auto-upload on selection */
  autoUpload?: boolean;
  /** Chunk size for large files */
  chunkSize?: number;
}

/**
 * File search/filter parameters
 */
export interface FileSearchParams {
  /** Search query (filename) */
  query?: string;
  /** Filter by content type */
  content_type?: string;
  /** Filter by file extension */
  extension?: string;
  /** Filter by user ID */
  user_id?: number;
  /** Filter by date range (from) */
  created_after?: ISODateString;
  /** Filter by date range (to) */
  created_before?: ISODateString;
  /** Sort field */
  sort_by?: "filename" | "created_at" | "content_type";
  /** Sort direction */
  sort_order?: "asc" | "desc";
}

/**
 * File download request
 */
export interface FileDownloadRequest {
  /** File ID */
  file_id: number;
  /** Optional filename override */
  filename?: string;
  /** Whether to force download vs inline display */
  download?: boolean;
}

/**
 * File deletion request
 */
export interface FileDeleteRequest {
  /** File ID */
  file_id: number;
  /** Optional reason for deletion */
  reason?: string;
}

/**
 * Bulk file operations
 */
export interface BulkFileOperation {
  /** Array of file IDs */
  file_ids: number[];
  /** Operation type */
  operation: "delete" | "archive" | "restore";
  /** Optional reason/note */
  reason?: string;
}

/**
 * File sharing configuration
 */
export interface FileSharing {
  /** File ID */
  file_id: number;
  /** Whether file is public */
  is_public: boolean;
  /** Shared with specific users */
  shared_users?: number[];
  /** Share expiry date */
  expires_at?: ISODateString;
  /** Share password protection */
  password?: string;
}

/**
 * File metadata update request
 */
export interface FileUpdateRequest {
  /** File ID */
  file_id: number;
  /** Updated filename */
  filename?: string;
  /** Updated metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Upload error types
 */
export enum UploadErrorType {
  FILE_TOO_LARGE = "file_too_large",
  INVALID_FILE_TYPE = "invalid_file_type",
  UPLOAD_FAILED = "upload_failed",
  NETWORK_ERROR = "network_error",
  SERVER_ERROR = "server_error",
  CANCELLED = "cancelled",
  QUOTA_EXCEEDED = "quota_exceeded",
  VIRUS_DETECTED = "virus_detected",
  INVALID_FILENAME = "invalid_filename",
  DUPLICATE_FILE = "duplicate_file",
  UNKNOWN = "unknown",
}

/**
 * Upload error
 */
export interface UploadError {
  /** Error type */
  type: UploadErrorType;
  /** Error message */
  message: string;
  /** File that caused the error */
  filename?: string;
  /** Additional error details */
  details?: Record<string, unknown>;
}

/**
 * Supported file types
 */
export const SUPPORTED_FILE_TYPES = {
  // Documents
  PDF: "application/pdf",
  DOC: "application/msword",
  DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  TXT: "text/plain",

  // Images
  JPEG: "image/jpeg",
  PNG: "image/png",
  GIF: "image/gif",
  SVG: "image/svg+xml",

  // Archives
  ZIP: "application/zip",
  RAR: "application/x-rar-compressed",

  // Data
  CSV: "text/csv",
  JSON: "application/json",
  XML: "application/xml",
} as const;

/**
 * File type categories
 */
export const FILE_TYPE_CATEGORIES = {
  DOCUMENT: [
    SUPPORTED_FILE_TYPES.PDF,
    SUPPORTED_FILE_TYPES.DOC,
    SUPPORTED_FILE_TYPES.DOCX,
    SUPPORTED_FILE_TYPES.TXT,
  ],
  IMAGE: [
    SUPPORTED_FILE_TYPES.JPEG,
    SUPPORTED_FILE_TYPES.PNG,
    SUPPORTED_FILE_TYPES.GIF,
    SUPPORTED_FILE_TYPES.SVG,
  ],
  ARCHIVE: [SUPPORTED_FILE_TYPES.ZIP, SUPPORTED_FILE_TYPES.RAR],
  DATA: [
    SUPPORTED_FILE_TYPES.CSV,
    SUPPORTED_FILE_TYPES.JSON,
    SUPPORTED_FILE_TYPES.XML,
  ],
} as const;

/**
 * Default upload configuration
 */
export const DEFAULT_UPLOAD_CONFIG: FileUploadConfig = {
  multiple: true,
  accept: Object.values(SUPPORTED_FILE_TYPES),
  maxSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 10,
  autoUpload: false,
  chunkSize: 1024 * 1024, // 1MB chunks
};

/**
 * Type guard for Upload
 */
export function isUpload(value: unknown): value is Upload {
  if (
    typeof value !== "object" ||
    value === null ||
    !("id" in value) ||
    !("name" in value) ||
    !("status" in value) ||
    !("progress" in value) ||
    !("createdAt" in value) ||
    typeof (value as Record<string, unknown>).id !== "string" ||
    typeof (value as Record<string, unknown>).name !== "string" ||
    typeof (value as Record<string, unknown>).progress !== "number" ||
    typeof (value as Record<string, unknown>).createdAt !== "string"
  ) {
    return false;
  }

  // Validate status is one of the allowed values
  const validStatuses: UploadStatus[] = [
    "pending",
    "uploading",
    "completed",
    "error",
    "cancelled",
  ];
  return validStatuses.includes(
    (value as Record<string, unknown>).status as UploadStatus,
  );
}

/**
 * Type guard for File
 */
export function isFile(value: unknown): value is File {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "filename" in value &&
    "content_type" in value &&
    "user_id" in value &&
    typeof (value as Record<string, unknown>).id === "number" &&
    typeof (value as Record<string, unknown>).filename === "string"
  );
}

/**
 * Type guard for UploadError
 */
export function isUploadError(error: unknown): error is UploadError {
  return (
    typeof error === "object" &&
    error !== null &&
    "type" in error &&
    "message" in error &&
    Object.values(UploadErrorType).includes(
      (error as Record<string, unknown>).type as UploadErrorType,
    )
  );
}

/**
 * Utility to get file extension from filename
 */
export function getFileExtension(filename: string): string {
  const lastDot = filename.lastIndexOf(".");
  return lastDot === -1 ? "" : filename.substring(lastDot + 1).toLowerCase();
}

/**
 * Utility to get file category from MIME type
 */
export function getFileCategory(
  contentType: string,
): keyof typeof FILE_TYPE_CATEGORIES | "OTHER" {
  for (const [category, types] of Object.entries(FILE_TYPE_CATEGORIES)) {
    if ((types as readonly string[]).includes(contentType)) {
      return category as keyof typeof FILE_TYPE_CATEGORIES;
    }
  }
  return "OTHER";
}

/**
 * Utility to format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";

  const units = ["B", "KB", "MB", "GB", "TB"];
  const digitGroups = Math.floor(Math.log(bytes) / Math.log(1024));

  return `${(bytes / 1024 ** digitGroups).toFixed(1)} ${units[digitGroups]}`;
}

/**
 * Utility to validate file type
 */
export function isValidFileType(
  file: globalThis.File,
  allowedTypes: string[],
): boolean {
  return allowedTypes.includes(file.type) || allowedTypes.includes("*/*");
}

/**
 * Utility to validate file size
 */
export function isValidFileSize(
  file: globalThis.File,
  maxSize: number,
): boolean {
  return file.size <= maxSize;
}

/**
 * Utility to create upload from File
 */
export function createUploadFromFile(file: globalThis.File): Upload {
  return {
    id: crypto.randomUUID(),
    name: file.name,
    status: "pending",
    progress: 0,
    createdAt: new Date().toISOString(),
    size: file.size,
    type: file.type,
  };
}

/**
 * Utility to check if upload is in progress
 */
export function isUploadInProgress(upload: Upload): boolean {
  return upload.status === "uploading" || upload.status === "pending";
}

/**
 * Utility to check if upload is completed
 */
export function isUploadCompleted(upload: Upload): boolean {
  return upload.status === "completed";
}

/**
 * Utility to check if upload is failed
 */
export function isUploadFailed(upload: Upload): boolean {
  return upload.status === "error";
}

/**
 * Utility to format upload size (alias for formatFileSize)
 */
export function formatUploadSize(bytes: number): string {
  return formatFileSize(bytes);
}

/**
 * Utility to calculate upload progress percentage
 */
export function calculateUploadProgress(
  uploadedOrUpload: number | Upload,
  total?: number,
): number {
  if (typeof uploadedOrUpload === "number") {
    // Called with (uploaded, total) parameters
    const uploaded = uploadedOrUpload;
    if (!total || total <= 0) {
      // Edge case: if total is 0 but we have uploaded data, consider it complete
      return uploaded > 0 ? 100 : 0;
    }
    return Math.round((uploaded / total) * 100);
  } else {
    // Called with Upload object
    const upload = uploadedOrUpload;
    if (!upload.progress) return 0;
    return Math.min(Math.max(upload.progress, 0), 100);
  }
}

/**
 * Utility to validate upload status
 */
export function validateUploadStatus(status: string): status is UploadStatus {
  const validStatuses: UploadStatus[] = [
    "pending",
    "uploading",
    "completed",
    "error",
    "cancelled",
  ];
  return validStatuses.includes(status as UploadStatus);
}

/**
 * Advanced upload types for Phase 5 implementation
 */

/**
 * Chunked upload configuration
 */
export interface ChunkedUploadConfig {
  /** Chunk size in bytes (default: 1MB) */
  chunkSize: number;
  /** Maximum number of concurrent chunks */
  maxConcurrentChunks: number;
  /** Maximum retry attempts per chunk */
  maxRetries: number;
  /** Retry delay in milliseconds */
  retryDelay: number;
}

/**
 * Upload chunk information
 */
export interface UploadChunk {
  /** Chunk index */
  index: number;
  /** Chunk start byte */
  start: number;
  /** Chunk end byte */
  end: number;
  /** Chunk size in bytes */
  size: number;
  /** Upload status */
  status: "pending" | "uploading" | "completed" | "error";
  /** Upload progress (0-100) */
  progress: number;
  /** Error message if failed */
  error?: string;
  /** Retry count */
  retryCount: number;
  /** ETag from server response */
  etag?: string;
}

/**
 * Upload session for resumable uploads
 */
export interface UploadSession {
  /** Session ID */
  id: string;
  /** File name */
  filename: string;
  /** Total file size */
  totalSize: number;
  /** Chunk size */
  chunkSize: number;
  /** Total number of chunks */
  totalChunks: number;
  /** Uploaded chunks */
  chunks: UploadChunk[];
  /** Session status */
  status: "active" | "paused" | "completed" | "cancelled" | "error";
  /** Creation timestamp */
  createdAt: ISODateString;
  /** Last update timestamp */
  updatedAt: ISODateString;
  /** Upload URL */
  uploadUrl?: string;
  /** File hash for integrity check */
  fileHash?: string;
}

/**
 * Enhanced upload types for Phase 5.2 File Upload Interface
 */

/**
 * Upload queue item for advanced queue management
 */
export interface UploadQueueItem {
  /** Unique queue item ID */
  id: string;
  /** File object */
  file: globalThis.File;
  /** Upload priority (higher = processed first) */
  priority: number;
  /** Upload status */
  status: UploadStatus;
  /** Upload progress */
  progress: UploadProgress;
  /** Validation result */
  validation?: FileValidationResult;
  /** Number of retry attempts */
  retryCount: number;
  /** Maximum retry attempts */
  maxRetries: number;
  /** Queue timestamp */
  queuedAt: Date;
  /** Upload start timestamp */
  startedAt?: Date;
  /** Upload completion timestamp */
  completedAt?: Date;
  /** Error information */
  error?: UploadError;
  /** Result after successful upload */
  result?: FileUploadResponse;
  /** Chunk information for chunked uploads */
  chunks?: UploadChunkInfo[];
}

/**
 * Upload chunk information for progress tracking
 */
export interface UploadChunkInfo {
  /** Chunk index */
  index: number;
  /** Chunk start byte */
  start: number;
  /** Chunk end byte */
  end: number;
  /** Chunk size in bytes */
  size: number;
  /** Upload status */
  status: "pending" | "uploading" | "completed" | "error";
  /** Upload progress (0-100) */
  progress: number;
  /** Error message if failed */
  error?: string;
  /** Retry count */
  retryCount: number;
  /** ETag from server response */
  etag?: string;
}

/**
 * Progress information for individual file chunks
 */
export interface ChunkProgress {
  /** Chunk index */
  index: number;
  /** Bytes transferred for this chunk */
  bytesTransferred: number;
  /** Total bytes in this chunk */
  totalBytes: number;
  /** Whether this chunk is complete */
  isComplete: boolean;
  /** Error if chunk failed */
  error?: string;
}

/**
 * Overall upload progress information
 */
export interface UploadProgress {
  /** Total bytes transferred */
  bytesTransferred: number;
  /** Total bytes to transfer */
  totalBytes: number;
  /** Progress percentage (0-100) */
  percentage: number;
  /** Number of chunks completed */
  chunksCompleted: number;
  /** Total number of chunks */
  totalChunks: number;
  /** Whether upload is complete */
  isComplete: boolean;
  /** Upload start time */
  startTime: number | null;
  /** Upload end time */
  endTime: number | null;
}

/**
 * File validation result
 */
export interface FileValidationResult {
  /** Whether file is valid */
  isValid: boolean;
  /** Validation errors */
  errors: FileValidationError[];
  /** Validation warnings */
  warnings: FileValidationWarning[];
  /** File metadata extracted during validation */
  metadata?: FileMetadataExtract;
}

/**
 * File validation error
 */
export interface FileValidationError {
  /** Error code */
  code: string;
  /** Human-readable error message */
  message: string;
  /** Field that caused the error */
  field: string;
  /** Error severity */
  severity: "error" | "warning";
}

/**
 * File validation warning (subset of error)
 */
export interface FileValidationWarning
  extends Omit<FileValidationError, "severity"> {
  severity: "warning";
}

/**
 * File metadata extracted during validation
 */
export interface FileMetadataExtract {
  /** File dimensions (for images) */
  dimensions?: { width: number; height: number };
  /** Number of pages (for documents) */
  pageCount?: number;
  /** Document title */
  title?: string;
  /** Author information */
  author?: string;
  /** Creation date */
  createdDate?: Date;
  /** Modified date */
  modifiedDate?: Date;
  /** Content preview/summary */
  preview?: string;
}

/**
 * File type category for easier grouping
 */
export type FileTypeCategory =
  | "document"
  | "image"
  | "archive"
  | "data"
  | "other";

/**
 * Upload queue configuration
 */
export interface UploadQueueConfig {
  /** Maximum number of concurrent uploads */
  maxConcurrent: number;
  /** Maximum number of retry attempts */
  maxRetries: number;
  /** Retry delay in milliseconds */
  retryDelay: number;
  /** Whether to automatically retry failed uploads */
  autoRetry: boolean;
  /** Whether to pause queue on error */
  pauseOnError: boolean;
}

/**
 * Advanced file upload options
 */
export interface AdvancedUploadOptions {
  /** Enable chunked upload for large files */
  enableChunked: boolean;
  /** Chunk size in bytes */
  chunkSize: number;
  /** Maximum concurrent chunks */
  maxConcurrentChunks: number;
  /** Enable background upload */
  enableBackground: boolean;
  /** Upload priority */
  priority: number;
  /** Custom metadata to attach */
  metadata?: Record<string, unknown>;
  /** Progress callback */
  onProgress?: (progress: number, speed: number, eta: number) => void;
  /** Chunk complete callback */
  onChunkComplete?: (chunkIndex: number, totalChunks: number) => void;
}

/**
 * File preview information
 */
export interface FilePreviewInfo {
  /** Whether preview is available */
  available: boolean;
  /** Preview type */
  type: "image" | "pdf" | "text" | "video" | "audio" | "none";
  /** Preview URL or data */
  url?: string;
  /** Preview thumbnail URL */
  thumbnailUrl?: string;
  /** Preview dimensions */
  dimensions?: {
    width: number;
    height: number;
  };
}

/**
 * Enhanced file management types for dashboard
 */

/**
 * File management dashboard state
 */
export interface FileManagementState {
  /** Selected file identifiers for bulk operations (can be IDs or filenames depending on API) */
  selectedFiles: string[];
  /** Current view mode */
  viewMode: "list" | "grid" | "table";
  /** Current filter configuration */
  filters: FileSearchParams;
  /** Current sort configuration */
  sort: {
    field: FileSearchParams["sort_by"];
    order: FileSearchParams["sort_order"];
  };
  /** Bulk operation state */
  bulkOperation: {
    type: BulkFileOperation["operation"] | null;
    inProgress: boolean;
    error: string | null;
  };
}

/**
 * File action result
 */
export interface FileActionResult {
  /** Success status */
  success: boolean;
  /** Success/error message */
  message: string;
  /** Affected file count */
  count?: number;
  /** File identifiers that were processed (can be IDs or filenames) */
  processedIds?: string[];
  /** File identifiers that failed (can be IDs or filenames) */
  failedIds?: string[];
}

/**
 * File preview configuration
 */
export interface FilePreviewConfig {
  /** File ID to preview */
  fileId: number;
  /** Preview type */
  type: "pdf" | "image" | "text" | "video" | "audio" | "unsupported";
  /** File URL for preview */
  url: string;
  /** File metadata */
  metadata: {
    filename: string;
    size: number;
    contentType: string;
    createdAt: ISODateString;
  };
}

/**
 * Real-time file update event
 */
export interface FileUpdateEvent {
  /** Event type */
  type:
    | "file_created"
    | "file_updated"
    | "file_deleted"
    | "file_shared"
    | "upload_progress";
  /** File ID */
  fileId: number;
  /** Updated file data */
  data: Partial<File>;
  /** Timestamp of the event */
  timestamp: ISODateString;
  /** User who triggered the event */
  userId?: number;
}

/**
 * File management dashboard configuration
 */
export interface FileManagementConfig {
  /** Items per page */
  pageSize: number;
  /** Enable real-time updates */
  realTimeUpdates: boolean;
  /** Enable bulk operations */
  bulkOperations: boolean;
  /** Enable file previews */
  previews: boolean;
  /** Maximum files for bulk operations */
  maxBulkSelection: number;
  /** Auto-refresh interval (ms) */
  refreshInterval?: number;
}
