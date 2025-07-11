import logger from '@/logger';

/**
 * Progress sample for speed calculation
 */
export interface ProgressSample {
    timestamp: number;
    bytesTransferred: number;
}

/**
 * Speed calculation result
 */
export interface SpeedCalculation {
    /** Current speed in bytes per second */
    speed: number;
    /** Average speed over the sample window */
    averageSpeed: number;
    /** Peak speed observed */
    peakSpeed: number;
    /** Whether calculation is stable (enough samples) */
    isStable: boolean;
}

/**
 * ETA calculation result
 */
export interface ETACalculation {
    /** Estimated time remaining in seconds */
    eta: number | null;
    /** Confidence level (0-1) */
    confidence: number;
    /** Whether ETA is stable */
    isStable: boolean;
    /** Completion percentage when ETA becomes stable */
    stableAtPercentage: number;
}

/**
 * Configuration for progress calculations
 */
export interface ProgressCalculationConfig {
    /** Number of samples to keep for calculations */
    maxSamples: number;
    /** Minimum samples required for stable calculation */
    minSamplesForStability: number;
    /** Sample window duration in milliseconds */
    sampleWindowMs: number;
    /** Minimum time elapsed before calculating ETA */
    minTimeForEta: number;
    /** Percentage threshold for stable ETA */
    etaStabilityThreshold: number;
}

/**
 * Progress calculation utilities for upload tracking
 */
export class ProgressCalculator {
    private samples: ProgressSample[] = [];
    private config: ProgressCalculationConfig;
    private peakSpeed = 0;
    private startTime: number | null = null;

    constructor(config: Partial<ProgressCalculationConfig> = {}) {
        this.config = {
            maxSamples: config.maxSamples || 20,
            minSamplesForStability: config.minSamplesForStability || 5,
            sampleWindowMs: config.sampleWindowMs || 30000, // 30 seconds
            minTimeForEta: config.minTimeForEta || 5000, // 5 seconds
            etaStabilityThreshold: config.etaStabilityThreshold || 10 // 10% completion
        };

        logger.debug('Progress calculator initialized', { config: this.config });
    }

    /**
     * Add a new progress sample
     */
    addSample(bytesTransferred: number, timestamp?: number): void {
        const now = timestamp || Date.now();

        if (!this.startTime) {
            this.startTime = now;
        }

        const sample: ProgressSample = {
            timestamp: now,
            bytesTransferred
        };

        this.samples.push(sample);

        // Remove old samples outside the window
        const cutoffTime = now - this.config.sampleWindowMs;
        this.samples = this.samples.filter(s => s.timestamp >= cutoffTime);

        // Keep only the max number of samples
        if (this.samples.length > this.config.maxSamples) {
            this.samples = this.samples.slice(-this.config.maxSamples);
        }

        logger.debug('Progress sample added', {
            bytesTransferred,
            timestamp: now,
            samplesCount: this.samples.length
        });
    }

    /**
     * Calculate current upload speed
     */
    calculateSpeed(): SpeedCalculation {
        if (this.samples.length < 2) {
            return {
                speed: 0,
                averageSpeed: 0,
                peakSpeed: this.peakSpeed,
                isStable: false
            };
        }

        // Calculate instantaneous speed (last two samples)
        const latest = this.samples[this.samples.length - 1];
        const previous = this.samples[this.samples.length - 2];
        const timeDiff = (latest.timestamp - previous.timestamp) / 1000; // seconds
        const bytesDiff = latest.bytesTransferred - previous.bytesTransferred;
        const instantSpeed = timeDiff > 0 ? bytesDiff / timeDiff : 0;

        // Calculate average speed over all samples
        const oldest = this.samples[0];
        const totalTimeDiff = (latest.timestamp - oldest.timestamp) / 1000;
        const totalBytesDiff = latest.bytesTransferred - oldest.bytesTransferred;
        const averageSpeed = totalTimeDiff > 0 ? totalBytesDiff / totalTimeDiff : 0;

        // Update peak speed
        if (instantSpeed > this.peakSpeed) {
            this.peakSpeed = instantSpeed;
        }

        const isStable = this.samples.length >= this.config.minSamplesForStability;

        const result = {
            speed: Math.max(0, instantSpeed),
            averageSpeed: Math.max(0, averageSpeed),
            peakSpeed: this.peakSpeed,
            isStable
        };

        logger.debug('Speed calculated', {
            instantSpeed: Math.round(instantSpeed),
            averageSpeed: Math.round(averageSpeed),
            peakSpeed: Math.round(this.peakSpeed),
            isStable,
            samplesCount: this.samples.length
        });

        return result;
    }

    /**
     * Calculate estimated time of arrival (ETA)
     */
    calculateETA(totalBytes: number, currentBytes: number): ETACalculation {
        if (this.samples.length < 2 || !this.startTime) {
            return {
                eta: null,
                confidence: 0,
                isStable: false,
                stableAtPercentage: 0
            };
        }

        const now = Date.now();
        const elapsedTime = (now - this.startTime) / 1000; // seconds
        const percentage = totalBytes > 0 ? (currentBytes / totalBytes) * 100 : 0;
        const remainingBytes = totalBytes - currentBytes;

        // Don't calculate ETA too early
        if (elapsedTime < this.config.minTimeForEta / 1000) {
            return {
                eta: null,
                confidence: 0,
                isStable: false,
                stableAtPercentage: 0
            };
        }

        const speedCalc = this.calculateSpeed();

        if (speedCalc.averageSpeed <= 0 || remainingBytes <= 0) {
            return {
                eta: null,
                confidence: 0,
                isStable: false,
                stableAtPercentage: 0
            };
        }

        // Use average speed for more stable ETA
        const eta = remainingBytes / speedCalc.averageSpeed;

        // Calculate confidence based on speed stability and completion percentage
        let confidence = 0;
        if (speedCalc.isStable) {
            confidence = Math.min(1, percentage / 50); // Confidence increases with completion
        } else {
            confidence = Math.min(0.5, percentage / 100); // Lower confidence for unstable speed
        }

        const isStable = speedCalc.isStable && percentage >= this.config.etaStabilityThreshold;

        const result = {
            eta,
            confidence,
            isStable,
            stableAtPercentage: this.config.etaStabilityThreshold
        };

        logger.debug('ETA calculated', {
            eta: Math.round(eta),
            confidence: Math.round(confidence * 100),
            isStable,
            percentage: Math.round(percentage),
            remainingBytes,
            averageSpeed: Math.round(speedCalc.averageSpeed)
        });

        return result;
    }

    /**
     * Get time-based statistics
     */
    getTimeStats(): {
        elapsedTime: number;
        estimatedTotalTime: number | null;
        completionTimestamp: number | null;
    } {
        if (!this.startTime) {
            return {
                elapsedTime: 0,
                estimatedTotalTime: null,
                completionTimestamp: null
            };
        }

        const now = Date.now();
        const elapsedTime = (now - this.startTime) / 1000;

        // Calculate estimated total time if we have enough data
        let estimatedTotalTime: number | null = null;
        let completionTimestamp: number | null = null;

        if (this.samples.length >= 2) {
            const latest = this.samples[this.samples.length - 1];
            const oldest = this.samples[0];
            const progressTime = (latest.timestamp - oldest.timestamp) / 1000;
            const progressBytes = latest.bytesTransferred - oldest.bytesTransferred;

            if (progressTime > 0 && progressBytes > 0) {
                const totalBytes = latest.bytesTransferred + (progressBytes * elapsedTime / progressTime);
                const rate = progressBytes / progressTime;

                if (rate > 0) {
                    estimatedTotalTime = totalBytes / rate;
                    completionTimestamp = this.startTime + (estimatedTotalTime * 1000);
                }
            }
        }

        return {
            elapsedTime,
            estimatedTotalTime,
            completionTimestamp
        };
    }

    /**
     * Reset all calculations
     */
    reset(): void {
        this.samples = [];
        this.peakSpeed = 0;
        this.startTime = null;

        logger.debug('Progress calculator reset');
    }

    /**
     * Get current sample count
     */
    getSampleCount(): number {
        return this.samples.length;
    }

    /**
     * Check if calculator has enough data for stable calculations
     */
    isStable(): boolean {
        return this.samples.length >= this.config.minSamplesForStability;
    }

    /**
     * Export samples for debugging
     */
    exportSamples(): ProgressSample[] {
        return [...this.samples];
    }
}

/**
 * Format bytes to human readable string
 */
export function formatBytes(bytes: number, decimals = 2): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

/**
 * Format speed to human readable string
 */
export function formatSpeed(bytesPerSecond: number, decimals = 1): string {
    return `${formatBytes(bytesPerSecond, decimals)}/s`;
}

/**
 * Format duration to human readable string
 */
export function formatDuration(seconds: number): string {
    if (seconds < 0) return '∞';
    if (seconds === 0) return '0s';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    const parts: string[] = [];

    if (hours > 0) {
        parts.push(`${hours}h`);
    }
    if (minutes > 0) {
        parts.push(`${minutes}m`);
    }
    if (secs > 0 || parts.length === 0) {
        parts.push(`${secs}s`);
    }

    return parts.join(' ');
}

/**
 * Format percentage with specified decimal places
 */
export function formatPercentage(percentage: number, decimals = 1): string {
    return `${percentage.toFixed(decimals)}%`;
}

/**
 * Calculate estimated completion time
 */
export function calculateCompletionTime(startTime: number, percentage: number): Date | null {
    if (percentage <= 0 || percentage >= 100) {
        return null;
    }

    const elapsed = Date.now() - startTime;
    const totalEstimated = elapsed / (percentage / 100);
    const remaining = totalEstimated - elapsed;

    return new Date(Date.now() + remaining);
}

/**
 * Smooth progress value to reduce jitter
 */
export function smoothProgress(currentProgress: number, targetProgress: number, smoothingFactor = 0.8): number {
    return currentProgress + (targetProgress - currentProgress) * smoothingFactor;
}

/**
 * Create a new progress calculator instance
 */
export function createProgressCalculator(config?: Partial<ProgressCalculationConfig>): ProgressCalculator {
    return new ProgressCalculator(config);
}
