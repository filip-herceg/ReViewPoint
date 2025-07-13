import { Loader2, Plus, Upload } from "lucide-react";
import type React from "react";
import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
	useAdvancedFileUpload,
	useFileValidation,
	useUploadProgress,
} from "@/hooks/uploads";
import type {
	FileValidationResult,
	UploadProgress,
	UploadQueueItem,
} from "@/lib/api/types/upload";
import { cn } from "@/lib/utils";

// --- Types ---

export interface AdvancedFileUploadProps {
	maxSize?: number;
	accept?: string[];
	maxFiles?: number;
	multiple?: boolean;
	dragAndDrop?: boolean;
	showProgress?: boolean;
	showValidation?: boolean;
	autoUpload?: boolean;
	className?: string;
	variant?: "default" | "compact" | "minimal";
	onFilesSelected?: (files: File[]) => void;
	onUploadStart?: (item: UploadQueueItem) => void;
	onUploadProgress?: (item: UploadQueueItem) => void;
	onUploadComplete?: (item: UploadQueueItem) => void;
	onUploadError?: (item: UploadQueueItem, error: Error) => void;
	onFilesRemoved?: (fileIds: string[]) => void;
	customValidation?: (file: File) => Promise<FileValidationResult>;
	disabled?: boolean;
	loading?: boolean;
}

// Fallback FileItem component (replace with real one if available)
interface FileItemProps {
	file: File;
	validation?: FileValidationResult;
	progress?: UploadProgress | number;
	status?: string;
	onRemove: () => void;
	showValidation?: boolean;
	showProgress?: boolean;
}

const FileItem = ({
	file,
	validation: _validation,
	progress: _progress,
	status: _status,
	onRemove,
	showValidation: _showValidation,
	showProgress: _showProgress,
}: FileItemProps) => (
	<div className="flex items-center gap-2 border rounded p-2">
		<span>{file.name}</span>
		<button type="button" onClick={onRemove}>
			Remove
		</button>
	</div>
);

const AdvancedFileUpload: React.FC<AdvancedFileUploadProps> = (props) => {
	const {
		maxSize = 10485760,
		accept = ["*/*"],
		maxFiles = 10,
		multiple = true,
		dragAndDrop = true,
		showProgress = true,
		showValidation = true,
		autoUpload = false,
		className,
		variant = "default",
		onFilesSelected,
		onUploadStart: _onUploadStart,
		onUploadProgress,
		onUploadComplete,
		onUploadError,
		onFilesRemoved,
		customValidation: _customValidation,
		disabled = false,
		loading = false,
	} = props;
	// State and refs
	const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
	const [fileValidations, setFileValidations] = useState<
		Map<string, FileValidationResult>
	>(new Map());
	const [isDragOver, setIsDragOver] = useState(false);
	const fileInputRef = useRef<HTMLInputElement>(null);

	// Upload hooks
	const {
		uploadSingleFile,
		uploadMultipleFiles,
		isUploading,
		error: _uploadError,
		cancelUpload: _cancelUpload,
		retryUpload: _retryUpload,
	} = useAdvancedFileUpload({
		enableChunked: true,
		chunkSize: 1024 * 1024,
		maxConcurrentChunks: 3,
		enableBackground: false,
		priority: 5,
	});

	const { validateFile: _validateFile } = useFileValidation({
		maxSize,
		allowedTypes: accept,
		maxFiles,
		enableContentValidation: true,
		enableSecurityScan: true,
	});

	const {
		progressState,
		initializeFileProgress,
		updateChunkProgress,
		getFileProgress: _getFileProgress,
		startTracking,
		stopTracking,
		resetProgress: _resetProgress,
		formatBytes: _formatBytes,
		formatSpeed: _formatSpeed,
		formatDuration: _formatDuration,
	} = useUploadProgress();

	// Dropzone classes utility
	const baseClasses =
		"flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-8 transition-all cursor-pointer";
	const getDropzoneClasses = useCallback(() => {
		if (isDragOver) {
			return cn(baseClasses, "border-primary bg-primary/10");
		}
		switch (variant) {
			case "compact":
				return cn(
					baseClasses,
					"border-border hover:border-primary cursor-pointer p-4",
				);
			case "minimal":
				return cn(
					baseClasses,
					"border-border hover:border-primary cursor-pointer p-2",
				);
			default:
				return cn(
					baseClasses,
					"border-border hover:border-primary cursor-pointer p-8",
				);
		}
	}, [isDragOver, variant]);

	// File picker
	const openFilePicker = useCallback(() => {
		fileInputRef.current?.click();
	}, []);

	// Clear files
	const clearFiles = useCallback(() => {
		setSelectedFiles([]);
		setFileValidations(new Map());
	}, []);

	// Logger (fallback to console if not available)
	const logger = (window as unknown as { logger?: Console }).logger || console;

	// Utility: Generate unique file key
	const getFileKey = useCallback((file: File): string => {
		return `${file.name}-${file.size}-${file.lastModified}`;
	}, []);

	// Handle file selection logic
	const handleFileSelection = useCallback(
		async (files: File[]) => {
			if (files.length === 0) return;

			// TODO: Implement complete file selection logic
			// Validate files, update state, etc.
			const validFiles = files.filter((file) => file.size <= maxSize);
			setSelectedFiles((prev) => [...prev, ...validFiles]);

			if (onFilesSelected) {
				onFilesSelected(validFiles);
			}
		},
		[maxSize, onFilesSelected],
	);

	// restore all hooks, state, and logic here, using props as needed
	// ...

	// (rest of the file continues as previously restored)

	/**
	 * Handle file input change
	 */
	const handleInputChange = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>) => {
			const files = Array.from(event.target.files || []);
			if (files.length > 0) {
				handleFileSelection(files);
			}
			// Reset input value to allow selecting the same file again
			event.target.value = "";
		},
		[handleFileSelection],
	);

	/**
	 * Handle drag and drop events
	 */
	const handleDragOver = useCallback(
		(event: React.DragEvent) => {
			if (!dragAndDrop || disabled || loading) return;

			event.preventDefault();
			event.stopPropagation();
			setIsDragOver(true);
		},
		[dragAndDrop, disabled, loading],
	);

	const handleDragLeave = useCallback(
		(event: React.DragEvent) => {
			if (!dragAndDrop) return;

			event.preventDefault();
			event.stopPropagation();
			setIsDragOver(false);
		},
		[dragAndDrop],
	);

	const handleDrop = useCallback(
		(event: React.DragEvent) => {
			if (!dragAndDrop || disabled || loading) return;

			event.preventDefault();
			event.stopPropagation();
			setIsDragOver(false);

			const files = Array.from(event.dataTransfer.files);
			if (files.length > 0) {
				handleFileSelection(files);
			}
		},
		[dragAndDrop, disabled, loading, handleFileSelection],
	);

	/**
	 * Handle file removal
	 */
	const handleRemoveFile = useCallback(
		(file: File) => {
			const fileKey = getFileKey(file);

			setSelectedFiles((prev) => prev.filter((f) => getFileKey(f) !== fileKey));
			setFileValidations((prev) => {
				const newValidations = new Map(prev);
				newValidations.delete(fileKey);
				return newValidations;
			});

			onFilesRemoved?.([fileKey]);

			logger.info("File removed", { fileName: file.name });
		},
		[getFileKey, onFilesRemoved, logger.info],
	);

	/**
	 * Handle upload
	 */
	const handleUpload = useCallback(
		async (filesToUpload?: File[]) => {
			const files = filesToUpload || selectedFiles;
			const validFiles = files.filter((file) => {
				const validation = fileValidations.get(getFileKey(file));
				return validation?.isValid;
			});

			if (validFiles.length === 0) {
				logger.warn("No valid files to upload");
				return;
			}

			try {
				startTracking();

				if (validFiles.length === 1) {
					const file = validFiles[0];
					const fileKey = getFileKey(file);

					// Initialize progress tracking
					initializeFileProgress(fileKey, file.size, 1);

					const queueItem = await uploadSingleFile(file, {
						onProgress: (progress: number, _speed: number, _eta: number) => {
							// Update chunk progress for better tracking
							updateChunkProgress(fileKey, 0, {
								index: 0,
								bytesTransferred: Math.round((file.size * progress) / 100),
								totalBytes: file.size,
								isComplete: progress >= 100,
							});

							// Update queue item with progress
							const progressObj: UploadProgress = {
								bytesTransferred: Math.round((file.size * progress) / 100),
								totalBytes: file.size,
								percentage: progress,
								chunksCompleted: progress >= 100 ? 1 : 0,
								totalChunks: 1,
								isComplete: progress >= 100,
								startTime: Date.now(),
								endTime: progress >= 100 ? Date.now() : null,
							};

							if (onUploadProgress) {
								onUploadProgress({
									...queueItem,
									progress: progressObj,
								});
							}
						},
					});

					if (onUploadComplete) {
						onUploadComplete(queueItem);
					}
				} else {
					// Multiple files upload
					await uploadMultipleFiles(validFiles);
				}
			} catch (error) {
				logger.error("Upload failed:", error);
				if (onUploadError) {
					onUploadError(
						{
							id: "error",
							file: validFiles[0],
							status: "error",
							progress: { percentage: 0, bytesTransferred: 0, totalBytes: 0 },
						} as UploadQueueItem,
						error as Error,
					);
				}
			} finally {
				stopTracking();
			}
		},
		[
			selectedFiles,
			fileValidations,
			getFileKey,
			logger,
			startTracking,
			initializeFileProgress,
			uploadSingleFile,
			updateChunkProgress,
			onUploadProgress,
			onUploadComplete,
			uploadMultipleFiles,
			onUploadError,
			stopTracking,
		],
	);

	const hasValidFiles = selectedFiles.some(
		(file) => fileValidations.get(getFileKey(file))?.isValid,
	);

	const hasInvalidFiles = selectedFiles.some(
		(file) => !fileValidations.get(getFileKey(file))?.isValid,
	);

	return (
		<div className={cn("space-y-4", className)}>
			{/* File input */}
			<input
				ref={fileInputRef}
				type="file"
				multiple={multiple}
				accept={accept.join(",")}
				onChange={handleInputChange}
				className="hidden"
				disabled={disabled || loading}
			/>
			{/* Drop zone */}
			<button
				type="button"
				className={getDropzoneClasses()}
				onDragOver={handleDragOver}
				onDragLeave={handleDragLeave}
				onDrop={handleDrop}
				onClick={openFilePicker}
				onKeyDown={(e) => {
					if (e.key === "Enter" || e.key === " ") {
						openFilePicker();
					}
				}}
			>
				<div className="text-center">
					<Upload
						className={cn(
							"mx-auto h-12 w-12 mb-4",
							disabled || loading ? "text-muted-foreground" : "text-primary",
						)}
					/>

					<div className="space-y-2">
						<p
							className={cn(
								"text-sm font-medium",
								disabled || loading
									? "text-muted-foreground"
									: "text-foreground",
							)}
						>
							{dragAndDrop
								? "Drag and drop files here, or click to browse"
								: "Click to browse files"}
						</p>

						<p className="text-xs text-muted-foreground">
							Supports {accept.join(", ")} • Max {maxFiles} files •{" "}
							{(maxSize / 1024 / 1024).toFixed(0)}MB per file
						</p>
					</div>
				</div>

				{loading && (
					<div className="absolute inset-0 bg-background bg-opacity-75 flex items-center justify-center rounded-lg">
						<Loader2 className="h-6 w-6 animate-spin text-primary" />
					</div>
				)}
			</button>

			{/* Selected files list */}
			{selectedFiles.length > 0 && (
				<div className="space-y-3">
					<div className="flex items-center justify-between">
						<h3 className="text-sm font-medium text-foreground">
							Selected Files ({selectedFiles.length})
						</h3>

						<Button
							variant="outline"
							size="sm"
							onClick={clearFiles}
							disabled={disabled || loading || isUploading}
						>
							Clear All
						</Button>
					</div>

					<div className="space-y-2">
						{selectedFiles.map((file) => {
							const fileKey = getFileKey(file);
							const validation = fileValidations.get(fileKey);
							const fileProgress = progressState.fileProgress.get(fileKey);

							return (
								<FileItem
									key={fileKey}
									file={file}
									validation={validation}
									progress={fileProgress?.percentage || 0}
									status={
										fileProgress?.isComplete
											? "completed"
											: fileProgress
												? "uploading"
												: validation?.isValid === false
													? "error"
													: "pending"
									}
									onRemove={() => handleRemoveFile(file)}
									showValidation={showValidation}
									showProgress={showProgress}
								/>
							);
						})}
					</div>
				</div>
			)}

			{/* Upload controls */}
			{selectedFiles.length > 0 && !autoUpload && (
				<div className="flex items-center justify-between pt-4 border-t border-border">
					<div className="text-sm text-muted-foreground">
						{hasValidFiles && (
							<span className="text-success-foreground">
								{
									selectedFiles.filter(
										(f) => fileValidations.get(getFileKey(f))?.isValid,
									).length
								}{" "}
								valid files
							</span>
						)}
						{hasValidFiles && hasInvalidFiles && (
							<span className="mx-2">•</span>
						)}
						{hasInvalidFiles && (
							<span className="text-destructive-foreground">
								{
									selectedFiles.filter(
										(f) => !fileValidations.get(getFileKey(f))?.isValid,
									).length
								}{" "}
								invalid files
							</span>
						)}
					</div>

					<Button
						onClick={() => handleUpload()}
						disabled={!hasValidFiles || disabled || loading || isUploading}
						className="min-w-[120px]"
					>
						{isUploading ? (
							<>
								<Loader2 className="h-4 w-4 mr-2 animate-spin text-primary" />
								Uploading...
							</>
						) : (
							<>
								<Plus className="h-4 w-4 mr-2 text-primary" />
								Upload Files
							</>
						)}
					</Button>
				</div>
			)}

			{/* Overall progress */}
			{showProgress && progressState.isTracking && (
				<div className="space-y-2 pt-4 border-t border-border">
					<div className="flex items-center justify-between text-sm">
						<span className="text-muted-foreground">Overall Progress</span>
						<span className="text-foreground font-medium">
							{progressState.overallProgress.percentage.toFixed(1)}%
						</span>
					</div>

					<Progress
						value={progressState.overallProgress.percentage}
						className="h-2"
					/>

					<div className="flex items-center justify-between text-xs text-muted-foreground">
						<span>
							Speed:{" "}
							{progressState.uploadSpeed > 0
								? `${(progressState.uploadSpeed / 1024 / 1024).toFixed(1)} MB/s`
								: "Calculating..."}
						</span>
						<span>
							ETA:{" "}
							{progressState.estimatedTimeRemaining
								? `${Math.round(progressState.estimatedTimeRemaining ?? 0)}s`
								: "Calculating..."}
						</span>
					</div>
				</div>
			)}
		</div>
	);
};

export default AdvancedFileUpload;
