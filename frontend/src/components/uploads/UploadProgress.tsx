import {
	AlertCircle,
	CheckCircle,
	Clock,
	FileText,
	TrendingUp,
	Upload,
	Zap,
} from "lucide-react";
import React, { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useUploadProgress } from "@/hooks/uploads";
import type { UploadProgress as UploadProgressType } from "@/lib/api/types/upload";
import { cn } from "@/lib/utils";

/**
 * Configuration for upload progress display
 */
export interface UploadProgressConfig {
	/** Show detailed progress information */
	showDetails?: boolean;
	/** Show individual file progress */
	showFileProgress?: boolean;
	/** Show speed and ETA */
	showMetrics?: boolean;
	/** Compact display mode */
	compact?: boolean;
	/** Show progress as percentage */
	showPercentage?: boolean;
	/** Show bytes transferred */
	showBytes?: boolean;
	/** Custom CSS classes */
	className?: string;
	/** Progress variant for styling */
	variant?: "default" | "success" | "warning" | "error";
}

/**
 * Props for the UploadProgress component
 */
export interface UploadProgressProps extends UploadProgressConfig {
	/** Custom title */
	title?: string;
	/** Custom progress data (overrides hook data) */
	progress?: UploadProgressType;
	/** File ID to show specific file progress */
	fileId?: string;
	/** Callback when progress completes */
	onComplete?: () => void;
}

/**
 * Individual file progress component
 */
interface FileProgressProps {
	fileId: string;
	fileName: string;
	progress: UploadProgressType;
	compact?: boolean;
	showMetrics?: boolean;
}

const FileProgress: React.FC<FileProgressProps> = ({
	fileId: _fileId,
	fileName,
	progress,
	compact = false,
	showMetrics = true,
}) => {
	const { formatBytes, formatDuration } = useUploadProgress();

	const isComplete = progress.isComplete;
	const hasError = progress.percentage === 0 && progress.endTime !== null;

	const getStatusIcon = () => {
		if (hasError) return <AlertCircle className="h-4 w-4 text-destructive" />;
		if (isComplete) return <CheckCircle className="h-4 w-4 text-success" />;
		return <Upload className="h-4 w-4 text-primary" />;
	};

	const _getProgressVariant = () => {
		if (hasError) return "error";
		if (isComplete) return "success";
		return "default";
	};

	return (
		<div className={cn("space-y-2", compact ? "py-2" : "py-3")}>
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2 min-w-0 flex-1">
					{getStatusIcon()}
					<span
						className={cn(
							"truncate",
							compact ? "text-sm" : "text-base",
							hasError ? "text-destructive-foreground" : "text-foreground",
						)}
					>
						{fileName}
					</span>
				</div>

				<Badge variant={isComplete ? "default" : "secondary"}>
					{progress.percentage.toFixed(1)}%
				</Badge>
			</div>

			<Progress value={progress.percentage} className="h-2" />

			{showMetrics && !compact && (
				<div className="flex items-center justify-between text-xs text-gray-500">
					<span>
						{formatBytes(progress.bytesTransferred)} /{" "}
						{formatBytes(progress.totalBytes)}
					</span>

					{progress.startTime && progress.endTime && (
						<span>
							Duration: {formatDuration(progress.endTime - progress.startTime)}
						</span>
					)}
				</div>
			)}
		</div>
	);
};

/**
 * Overall progress metrics component
 */
interface ProgressMetricsProps {
	uploadSpeed: number;
	estimatedTimeRemaining: number | null;
	formatSpeed: (bytesPerSecond: number) => string;
	formatDuration: (milliseconds: number) => string;
	compact?: boolean;
}

const ProgressMetrics: React.FC<ProgressMetricsProps> = ({
	uploadSpeed,
	estimatedTimeRemaining,
	formatSpeed,
	formatDuration,
	compact = false,
}) => {
	const metrics = [
		{
			icon: <Zap className="h-4 w-4 text-primary" />,
			label: "Speed",
			value: uploadSpeed > 0 ? formatSpeed(uploadSpeed) : "Calculating...",
			color: "text-primary",
		},
		{
			icon: <Clock className="h-4 w-4 text-success" />,
			label: "ETA",
			value:
				estimatedTimeRemaining !== null
					? formatDuration(estimatedTimeRemaining * 1000)
					: "Calculating...",
			color: "text-success",
		},
	];

	if (compact) {
		return (
			<div className="flex items-center gap-4 text-xs text-muted-foreground">
				{metrics.map((metric) => (
					<div key={metric.label} className="flex items-center gap-1">
						{metric.icon}
						<span>{metric.value}</span>
					</div>
				))}
			</div>
		);
	}

	return (
		<div className="grid grid-cols-2 gap-4">
			{metrics.map((metric) => (
				<div key={metric.label} className="flex items-center gap-2">
					<div className={cn("p-2 rounded-full bg-muted", metric.color)}>
						{metric.icon}
					</div>
					<div>
						<p className="text-xs text-muted-foreground">{metric.label}</p>
						<p className="text-sm font-medium text-foreground">
							{metric.value}
						</p>
					</div>
				</div>
			))}
		</div>
	);
};

/**
 * Upload Progress Component
 *
 * Displays upload progress with detailed metrics, file-specific progress,
 * and customizable display options.
 */
export const UploadProgress: React.FC<UploadProgressProps> = ({
	showDetails = true,
	showFileProgress = true,
	showMetrics = true,
	compact = false,
	showPercentage = true,
	showBytes = true,
	className,
	variant = "default",
	title = "Upload Progress",
	progress: customProgress,
	fileId,
	onComplete,
}) => {
	const {
		progressState,
		getFileProgress,
		getAllFileProgress,
		formatBytes,
		formatSpeed,
		formatDuration,
		uploadSpeed,
		estimatedTimeRemaining,
	} = useUploadProgress();

	// Determine which progress to show
	const displayProgress = useMemo(() => {
		if (customProgress) return customProgress;
		if (fileId) return getFileProgress(fileId);
		return progressState.overallProgress;
	}, [customProgress, fileId, getFileProgress, progressState.overallProgress]);

	// Get all file progress for detailed view
	const allFileProgress = getAllFileProgress();

	// Handle completion callback
	React.useEffect(() => {
		if (displayProgress?.isComplete && onComplete) {
			onComplete();
		}
	}, [displayProgress?.isComplete, onComplete]);

	// Don't render if no progress data
	if (!displayProgress || (!progressState.isTracking && !customProgress)) {
		return null;
	}

	const getVariantClasses = () => {
		switch (variant) {
			case "success":
				return "border-success/20 bg-success/10";
			case "warning":
				return "border-warning/20 bg-warning/10";
			case "error":
				return "border-destructive/20 bg-destructive/10";
			default:
				return "border-border bg-background";
		}
	};

	const _getProgressVariant = () => {
		if (displayProgress.isComplete) return "success";
		if (variant === "error") return "error";
		return "default";
	};

	if (compact) {
		return (
			<div
				className={cn(
					"flex items-center gap-4 p-3 rounded-lg border",
					getVariantClasses(),
					className,
				)}
			>
				<div className="flex items-center gap-2 min-w-0 flex-1">
					<Upload className="h-4 w-4 text-primary flex-shrink-0" />
					<div className="min-w-0 flex-1">
						<div className="flex items-center justify-between mb-1">
							<span className="text-sm font-medium text-foreground truncate">
								{title}
							</span>
							{showPercentage && (
								<span className="text-sm text-muted-foreground ml-2">
									{displayProgress.percentage.toFixed(1)}%
								</span>
							)}
						</div>
						<Progress value={displayProgress.percentage} className="h-1" />
					</div>
				</div>

				{showMetrics && (
					<ProgressMetrics
						uploadSpeed={uploadSpeed}
						estimatedTimeRemaining={estimatedTimeRemaining}
						formatSpeed={formatSpeed}
						formatDuration={formatDuration}
						compact={true}
					/>
				)}
			</div>
		);
	}

	return (
		<Card className={cn("w-full", getVariantClasses(), className)}>
			<CardContent className="p-6 space-y-4">
				{/* Header */}
				<div className="flex items-center justify-between">
					<div className="flex items-center gap-2">
						<Upload className="h-5 w-5 text-primary" />
						<h3 className="text-lg font-semibold text-foreground">{title}</h3>
					</div>

					{displayProgress.isComplete && (
						<Badge
							variant="default"
							className="bg-success/10 text-success-foreground"
						>
							<CheckCircle className="h-3 w-3 mr-1" />
							Complete
						</Badge>
					)}
				</div>

				{/* Main Progress */}
				<div className="space-y-2">
					<div className="flex items-center justify-between">
						{showPercentage && (
							<span className="text-2xl font-bold text-foreground">
								{displayProgress.percentage.toFixed(1)}%
							</span>
						)}

						{showBytes && (
							<span className="text-sm text-muted-foreground">
								{formatBytes(displayProgress.bytesTransferred)} /{" "}
								{formatBytes(displayProgress.totalBytes)}
							</span>
						)}
					</div>

					<Progress value={displayProgress.percentage} className="h-3" />
				</div>

				{/* Metrics */}
				{showMetrics && !displayProgress.isComplete && (
					<ProgressMetrics
						uploadSpeed={uploadSpeed}
						estimatedTimeRemaining={estimatedTimeRemaining}
						formatSpeed={formatSpeed}
						formatDuration={formatDuration}
						compact={false}
					/>
				)}

				{/* File Progress */}
				{showFileProgress && showDetails && allFileProgress.length > 1 && (
					<div className="space-y-3">
						<div className="flex items-center gap-2 pt-2 border-t">
							<FileText className="h-4 w-4 text-muted-foreground" />
							<span className="text-sm font-medium text-foreground">
								File Progress ({allFileProgress.length} files)
							</span>
						</div>

						<div className="space-y-2 max-h-40 overflow-y-auto">
							{allFileProgress.map(({ fileId, progress }) => (
								<FileProgress
									key={fileId}
									fileId={fileId}
									fileName={fileId.split("-")[0]} // Extract filename from fileId
									progress={progress}
									compact={true}
									showMetrics={false}
								/>
							))}
						</div>
					</div>
				)}

				{/* Completion Stats */}
				{displayProgress.isComplete && showDetails && (
					<div className="flex items-center justify-between pt-2 border-t text-sm text-muted-foreground">
						<div className="flex items-center gap-4">
							<span>
								<TrendingUp className="h-4 w-4 inline mr-1" />
								{displayProgress.totalChunks} chunks
							</span>
							<span>
								<FileText className="h-4 w-4 inline mr-1" />
								{formatBytes(displayProgress.totalBytes)}
							</span>
						</div>

						{displayProgress.startTime && displayProgress.endTime && (
							<span>
								Total time:{" "}
								{formatDuration(
									displayProgress.endTime - displayProgress.startTime,
								)}
							</span>
						)}
					</div>
				)}
			</CardContent>
		</Card>
	);
};

export default UploadProgress;
