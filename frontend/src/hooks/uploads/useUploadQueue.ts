import { useCallback, useRef, useState } from "react";
import type {
	UploadQueueConfig,
	UploadQueueItem,
} from "@/lib/api/types/upload";
import logger from "@/logger";

/**
 * Hook for managing upload queue operations
 */
export function useUploadQueue(config: Partial<UploadQueueConfig> = {}) {
	const [queue, setQueue] = useState<UploadQueueItem[]>([]);
	const [isProcessing, setIsProcessing] = useState(false);
	const processingRef = useRef<boolean>(false);

	const defaultConfig: UploadQueueConfig = {
		maxConcurrent: config.maxConcurrent || 3,
		maxRetries: config.maxRetries || 3,
		retryDelay: config.retryDelay || 1000,
		autoRetry: config.autoRetry ?? true,
		pauseOnError: config.pauseOnError ?? false,
	};

	/**
	 * Add item to upload queue
	 */
	const addToQueue = useCallback((item: UploadQueueItem) => {
		logger.info("Adding item to upload queue", {
			id: item.id,
			filename: item.file.name,
			priority: item.priority,
		});

		setQueue((currentQueue) => {
			// Insert item based on priority (higher priority first)
			const newQueue = [...currentQueue];
			const insertIndex = newQueue.findIndex(
				(queueItem) => queueItem.priority < item.priority,
			);

			if (insertIndex === -1) {
				newQueue.push(item);
			} else {
				newQueue.splice(insertIndex, 0, item);
			}

			logger.debug("Queue updated", {
				queueLength: newQueue.length,
				insertIndex: insertIndex === -1 ? newQueue.length - 1 : insertIndex,
			});

			return newQueue;
		});
	}, []);

	/**
	 * Update queue item
	 */
	const updateQueueItem = useCallback(
		(id: string, updates: Partial<UploadQueueItem>) => {
			setQueue((currentQueue) =>
				currentQueue.map((item) =>
					item.id === id ? { ...item, ...updates } : item,
				),
			);

			logger.debug("Queue item updated", { id, updates });
		},
		[],
	);

	/**
	 * Remove item from queue
	 */
	const removeFromQueue = useCallback((id: string) => {
		setQueue((currentQueue) => {
			const filteredQueue = currentQueue.filter((item) => item.id !== id);
			logger.info("Item removed from queue", {
				id,
				remainingItems: filteredQueue.length,
			});
			return filteredQueue;
		});
	}, []);

	/**
	 * Get queue item by ID
	 */
	const getQueueItem = useCallback(
		(id: string): UploadQueueItem | undefined => {
			return queue.find((item) => item.id === id);
		},
		[queue],
	);

	/**
	 * Get queue items by status
	 */
	const getQueueItemsByStatus = useCallback(
		(status: UploadQueueItem["status"]): UploadQueueItem[] => {
			return queue.filter((item) => item.status === status);
		},
		[queue],
	);

	/**
	 * Move item to different position in queue
	 */
	const moveQueueItem = useCallback((id: string, newIndex: number) => {
		setQueue((currentQueue) => {
			const itemIndex = currentQueue.findIndex((item) => item.id === id);
			if (itemIndex === -1 || newIndex < 0 || newIndex >= currentQueue.length) {
				logger.warn("Cannot move queue item - invalid index", {
					id,
					itemIndex,
					newIndex,
				});
				return currentQueue;
			}

			const newQueue = [...currentQueue];
			const [item] = newQueue.splice(itemIndex, 1);
			newQueue.splice(newIndex, 0, item);

			logger.info("Queue item moved", {
				id,
				fromIndex: itemIndex,
				toIndex: newIndex,
			});

			return newQueue;
		});
	}, []);

	/**
	 * Change item priority
	 */
	const changePriority = useCallback(
		(id: string, newPriority: number) => {
			updateQueueItem(id, { priority: newPriority });

			// Re-sort queue based on new priority
			setQueue((currentQueue) => {
				const sorted = [...currentQueue].sort(
					(a, b) => b.priority - a.priority,
				);
				logger.info("Queue re-sorted after priority change", {
					id,
					newPriority,
				});
				return sorted;
			});
		},
		[updateQueueItem],
	);

	/**
	 * Pause queue item
	 */
	const pauseQueueItem = useCallback(
		(id: string) => {
			updateQueueItem(id, { status: "paused" });
			logger.info("Queue item paused", { id });
		},
		[updateQueueItem],
	);

	/**
	 * Resume queue item
	 */
	const resumeQueueItem = useCallback(
		(id: string) => {
			updateQueueItem(id, { status: "pending" });
			logger.info("Queue item resumed", { id });
		},
		[updateQueueItem],
	);

	/**
	 * Cancel queue item
	 */
	const cancelQueueItem = useCallback(
		(id: string) => {
			updateQueueItem(id, {
				status: "cancelled",
				endTime: Date.now(),
			});
			logger.info("Queue item cancelled", { id });
		},
		[updateQueueItem],
	);

	/**
	 * Clear completed items from queue
	 */
	const clearCompleted = useCallback(() => {
		setQueue((currentQueue) => {
			const filteredQueue = currentQueue.filter(
				(item) => item.status !== "completed" && item.status !== "cancelled",
			);
			const removedCount = currentQueue.length - filteredQueue.length;

			if (removedCount > 0) {
				logger.info("Cleared completed items from queue", { removedCount });
			}

			return filteredQueue;
		});
	}, []);

	/**
	 * Clear all items from queue
	 */
	const clearQueue = useCallback(() => {
		setQueue([]);
		logger.info("Queue cleared");
	}, []);

	/**
	 * Retry failed items
	 */
	const retryFailedItems = useCallback(() => {
		const failedItems = getQueueItemsByStatus("error");

		failedItems.forEach((item) => {
			if (
				item.error?.retryable &&
				item.error.retryCount < defaultConfig.maxRetries
			) {
				updateQueueItem(item.id, {
					status: "pending",
					error: {
						...item.error,
						retryCount: item.error.retryCount + 1,
					},
				});

				logger.info("Retrying failed queue item", {
					id: item.id,
					retryCount: item.error.retryCount + 1,
				});
			}
		});
	}, [getQueueItemsByStatus, updateQueueItem, defaultConfig.maxRetries]);

	/**
	 * Process queue (start uploads)
	 */
	const processQueue = useCallback(async () => {
		if (processingRef.current) {
			logger.debug("Queue processing already in progress");
			return;
		}

		processingRef.current = true;
		setIsProcessing(true);

		try {
			logger.info("Starting queue processing");

			const pendingItems = getQueueItemsByStatus("pending");
			const uploadingItems = getQueueItemsByStatus("uploading");
			const availableSlots =
				defaultConfig.maxConcurrent - uploadingItems.length;

			if (availableSlots <= 0) {
				logger.debug("No available slots for new uploads", {
					maxConcurrent: defaultConfig.maxConcurrent,
					currentUploading: uploadingItems.length,
				});
				return;
			}

			const itemsToProcess = pendingItems.slice(0, availableSlots);

			logger.info("Processing queue items", {
				pendingCount: pendingItems.length,
				processingCount: itemsToProcess.length,
				availableSlots,
			});

			// Start processing items
			const processingPromises = itemsToProcess.map(async (item) => {
				try {
					updateQueueItem(item.id, {
						status: "uploading",
						startTime: Date.now(),
					});

					// This would typically trigger the actual upload
					// The upload logic is handled by useAdvancedFileUpload
					logger.debug("Queue item processing started", { id: item.id });
				} catch (error) {
					logger.error("Queue item processing failed", {
						id: item.id,
						error: error instanceof Error ? error.message : "Unknown error",
					});

					updateQueueItem(item.id, {
						status: "error",
						error: {
							message:
								error instanceof Error ? error.message : "Processing failed",
							code: "QUEUE_PROCESSING_ERROR",
							retryable: true,
							retryCount: 0,
						},
					});
				}
			});

			await Promise.allSettled(processingPromises);
		} catch (error) {
			logger.error("Queue processing failed", {
				error: error instanceof Error ? error.message : "Unknown error",
			});
		} finally {
			processingRef.current = false;
			setIsProcessing(false);
			logger.info("Queue processing completed");
		}
	}, [getQueueItemsByStatus, updateQueueItem, defaultConfig.maxConcurrent]);

	/**
	 * Get queue statistics
	 */
	const getQueueStats = useCallback(() => {
		const stats = {
			total: queue.length,
			pending: getQueueItemsByStatus("pending").length,
			uploading: getQueueItemsByStatus("uploading").length,
			completed: getQueueItemsByStatus("completed").length,
			error: getQueueItemsByStatus("error").length,
			cancelled: getQueueItemsByStatus("cancelled").length,
			paused: getQueueItemsByStatus("paused").length,
		};

		logger.debug("Queue statistics", stats);
		return stats;
	}, [queue.length, getQueueItemsByStatus]);

	return {
		// State
		queue,
		isProcessing,

		// Actions
		addToQueue,
		updateQueueItem,
		removeFromQueue,
		getQueueItem,
		getQueueItemsByStatus,
		moveQueueItem,
		changePriority,
		pauseQueueItem,
		resumeQueueItem,
		cancelQueueItem,
		clearCompleted,
		clearQueue,
		retryFailedItems,
		processQueue,

		// Utilities
		getQueueStats,
	};
}
