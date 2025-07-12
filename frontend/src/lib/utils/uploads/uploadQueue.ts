import type {
	UploadProgress,
	UploadQueueItem,
	UploadStatus,
} from "@/lib/api/types/upload";
import logger from "@/logger";

/**
 * Queue operation types
 */
export type QueueOperation =
	| "add"
	| "remove"
	| "update"
	| "reorder"
	| "clear"
	| "retry";

/**
 * Queue event data
 */
export interface QueueEvent {
	operation: QueueOperation;
	items: UploadQueueItem[];
	timestamp: Date;
}

/**
 * Queue configuration
 */
export interface QueueConfig {
	/** Maximum number of concurrent uploads */
	maxConcurrent: number;
	/** Maximum queue size */
	maxQueueSize: number;
	/** Default retry count */
	defaultRetries: number;
	/** Auto-start uploads */
	autoStart: boolean;
	/** Sort by priority */
	sortByPriority: boolean;
}

/**
 * Upload queue manager for handling multiple file uploads
 */
export class UploadQueue {
	private items: Map<string, UploadQueueItem> = new Map();
	private activeUploads: Set<string> = new Set();
	private eventListeners: Array<(event: QueueEvent) => void> = [];
	private config: QueueConfig;

	constructor(config: Partial<QueueConfig> = {}) {
		this.config = {
			maxConcurrent: config.maxConcurrent || 3,
			maxQueueSize: config.maxQueueSize || 100,
			defaultRetries: config.defaultRetries || 3,
			autoStart: config.autoStart ?? true,
			sortByPriority: config.sortByPriority ?? true,
		};

		logger.info("Upload queue initialized", { config: this.config });
	}

	/**
	 * Add file to upload queue
	 */
	add(file: File, options: Partial<UploadQueueItem> = {}): string {
		if (this.items.size >= this.config.maxQueueSize) {
			throw new Error(
				`Queue is full. Maximum size: ${this.config.maxQueueSize}`,
			);
		}

		const id = options.id || this.generateId();
		const queueItem: UploadQueueItem = {
			id,
			file,
			priority: options.priority || 0,
			status: "pending",
			progress: {
				bytesTransferred: 0,
				totalBytes: file.size,
				percentage: 0,
				chunksCompleted: 0,
				totalChunks: Math.ceil(file.size / (1024 * 1024)), // Assume 1MB chunks
				isComplete: false,
				startTime: null,
				endTime: null,
			},
			validation: options.validation,
			error: options.error,
			retryCount: 0,
			maxRetries: options.maxRetries || this.config.defaultRetries,
			queuedAt: new Date(),
			...options,
		};

		this.items.set(id, queueItem);
		this.emitEvent("add", [queueItem]);

		logger.debug("File added to queue", {
			id,
			fileName: file.name,
			fileSize: file.size,
			priority: queueItem.priority,
		});

		if (this.config.autoStart) {
			this.processNext();
		}

		return id;
	}

	/**
	 * Remove item from queue
	 */
	remove(id: string): boolean {
		const item = this.items.get(id);
		if (!item) {
			return false;
		}

		// Stop active upload if running
		if (this.activeUploads.has(id)) {
			this.activeUploads.delete(id);
		}

		this.items.delete(id);
		this.emitEvent("remove", [item]);

		logger.debug("File removed from queue", { id, fileName: item.file.name });

		// Process next item if we have capacity
		if (this.activeUploads.size < this.config.maxConcurrent) {
			this.processNext();
		}

		return true;
	}

	/**
	 * Update queue item
	 */
	update(id: string, updates: Partial<UploadQueueItem>): boolean {
		const item = this.items.get(id);
		if (!item) {
			return false;
		}

		const updatedItem = { ...item, ...updates };
		this.items.set(id, updatedItem);
		this.emitEvent("update", [updatedItem]);

		logger.debug("Queue item updated", {
			id,
			fileName: item.file.name,
			status: updatedItem.status,
			progress: updatedItem.progress.percentage,
		});

		return true;
	}

	/**
	 * Update item status
	 */
	updateStatus(id: string, status: UploadStatus, error?: Error): boolean {
		const item = this.items.get(id);
		const updates: Partial<UploadQueueItem> = { status };

		if (error && item) {
			updates.error = {
				type: "UPLOAD_FAILED" as any, // Using any temporarily since UploadErrorType may not have this value
				message: error.message,
				filename: item.file.name,
				details: {
					retryable: this.isRetryableError(error),
					timestamp: new Date(),
				},
			};
		}

		if (status === "uploading") {
			updates.startedAt = new Date();
			this.activeUploads.add(id);
		} else if (
			status === "completed" ||
			status === "error" ||
			status === "cancelled"
		) {
			updates.completedAt = new Date();
			this.activeUploads.delete(id);

			// Process next item if we have capacity
			if (this.activeUploads.size < this.config.maxConcurrent) {
				this.processNext();
			}
		}

		return this.update(id, updates);
	}

	/**
	 * Update item progress
	 */
	updateProgress(id: string, progress: Partial<UploadProgress>): boolean {
		const item = this.items.get(id);
		if (!item) {
			return false;
		}

		const updatedProgress = { ...item.progress, ...progress };
		return this.update(id, { progress: updatedProgress });
	}

	/**
	 * Retry failed upload
	 */
	retry(id: string): boolean {
		const item = this.items.get(id);
		if (!item || item.status !== "error") {
			return false;
		}

		if (item.retryCount >= item.maxRetries) {
			logger.warn("Maximum retries exceeded", {
				id,
				fileName: item.file.name,
				retryCount: item.retryCount,
				maxRetries: item.maxRetries,
			});
			return false;
		}

		const updates: Partial<UploadQueueItem> = {
			status: "pending",
			retryCount: item.retryCount + 1,
			error: undefined,
		};

		this.update(id, updates);
		this.emitEvent("retry", [{ ...item, ...updates }]);

		logger.info("Upload retry initiated", {
			id,
			fileName: item.file.name,
			retryCount: updates.retryCount,
		});

		if (this.config.autoStart) {
			this.processNext();
		}

		return true;
	}

	/**
	 * Get queue item
	 */
	get(id: string): UploadQueueItem | undefined {
		return this.items.get(id);
	}

	/**
	 * Get all queue items
	 */
	getAll(): UploadQueueItem[] {
		return Array.from(this.items.values());
	}

	/**
	 * Get items by status
	 */
	getByStatus(status: UploadStatus | UploadStatus[]): UploadQueueItem[] {
		const statuses = Array.isArray(status) ? status : [status];
		return this.getAll().filter((item) => statuses.includes(item.status));
	}

	/**
	 * Get pending items sorted by priority
	 */
	getPending(): UploadQueueItem[] {
		const pending = this.getByStatus("pending");

		if (this.config.sortByPriority) {
			return pending.sort((a, b) => {
				// Higher priority first, then FIFO for same priority
				if (a.priority !== b.priority) {
					return b.priority - a.priority;
				}
				return a.queuedAt.getTime() - b.queuedAt.getTime();
			});
		}

		return pending.sort((a, b) => a.queuedAt.getTime() - b.queuedAt.getTime());
	}

	/**
	 * Get active uploads
	 */
	getActive(): UploadQueueItem[] {
		return this.getByStatus("uploading");
	}

	/**
	 * Clear queue
	 */
	clear(includeActive = false): void {
		const allItems = this.getAll();

		if (includeActive) {
			this.items.clear();
			this.activeUploads.clear();
		} else {
			// Only remove non-active items
			const activeIds = new Set(this.activeUploads);
			for (const [id, _item] of this.items) {
				if (!activeIds.has(id)) {
					this.items.delete(id);
				}
			}
		}

		this.emitEvent("clear", allItems);
		logger.info("Queue cleared", {
			includeActive,
			remainingItems: this.items.size,
		});
	}

	/**
	 * Reorder queue item
	 */
	reorder(id: string, newPriority: number): boolean {
		const item = this.items.get(id);
		if (!item || item.status !== "pending") {
			return false;
		}

		const updated = this.update(id, { priority: newPriority });
		if (updated) {
			this.emitEvent("reorder", [{ ...item, priority: newPriority }]);
			logger.debug("Queue item reordered", {
				id,
				fileName: item.file.name,
				oldPriority: item.priority,
				newPriority,
			});
		}

		return updated;
	}

	/**
	 * Check if can start new upload
	 */
	canStartUpload(): boolean {
		return this.activeUploads.size < this.config.maxConcurrent;
	}

	/**
	 * Process next pending item
	 */
	processNext(): UploadQueueItem | null {
		if (!this.canStartUpload()) {
			return null;
		}

		const pending = this.getPending();
		if (pending.length === 0) {
			return null;
		}

		const nextItem = pending[0];
		this.updateStatus(nextItem.id, "uploading");

		logger.debug("Processing next upload", {
			id: nextItem.id,
			fileName: nextItem.file.name,
			priority: nextItem.priority,
			activeCount: this.activeUploads.size,
		});

		return nextItem;
	}

	/**
	 * Get queue statistics
	 */
	getStats() {
		const all = this.getAll();
		return {
			total: all.length,
			pending: this.getByStatus("pending").length,
			uploading: this.getByStatus("uploading").length,
			completed: this.getByStatus("completed").length,
			error: this.getByStatus("error").length,
			cancelled: this.getByStatus("cancelled").length,
			activeUploads: this.activeUploads.size,
			canStartMore: this.canStartUpload(),
			maxConcurrent: this.config.maxConcurrent,
			totalBytes: all.reduce((sum, item) => sum + item.file.size, 0),
			completedBytes: all
				.filter((item) => item.status === "completed")
				.reduce((sum, item) => sum + item.file.size, 0),
		};
	}

	/**
	 * Add event listener
	 */
	addEventListener(listener: (event: QueueEvent) => void): void {
		this.eventListeners.push(listener);
	}

	/**
	 * Remove event listener
	 */
	removeEventListener(listener: (event: QueueEvent) => void): void {
		const index = this.eventListeners.indexOf(listener);
		if (index > -1) {
			this.eventListeners.splice(index, 1);
		}
	}

	/**
	 * Update configuration
	 */
	updateConfig(config: Partial<QueueConfig>): void {
		this.config = { ...this.config, ...config };
		logger.info("Queue configuration updated", { config: this.config });
	}

	/**
	 * Generate unique ID
	 */
	private generateId(): string {
		return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
	}

	/**
	 * Emit queue event
	 */
	private emitEvent(operation: QueueOperation, items: UploadQueueItem[]): void {
		const event: QueueEvent = {
			operation,
			items,
			timestamp: new Date(),
		};

		this.eventListeners.forEach((listener) => {
			try {
				listener(event);
			} catch (error) {
				logger.error("Queue event listener error", { error, operation });
			}
		});
	}

	/**
	 * Check if error is retryable
	 */
	private isRetryableError(error: Error): boolean {
		const retryableMessages = [
			"network error",
			"timeout",
			"connection failed",
			"server error",
			"internal server error",
			"bad gateway",
			"service unavailable",
			"gateway timeout",
		];

		const message = error.message.toLowerCase();
		return retryableMessages.some((msg) => message.includes(msg));
	}
}

/**
 * Create a new upload queue instance
 */
export function createUploadQueue(config?: Partial<QueueConfig>): UploadQueue {
	return new UploadQueue(config);
}

/**
 * Default upload queue instance
 */
export const defaultUploadQueue = createUploadQueue();
