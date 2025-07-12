import {
	Download,
	Eye,
	FileText,
	MoreVertical,
	Share2,
	Trash2,
} from "lucide-react";
import type React from "react";
import { Button } from "@/components/ui/button";
import type { FileItem } from "@/lib/store/fileManagementStore";
import { cn } from "@/lib/utils";
import {
	formatFileSize as formatFileSizeUtil,
	getFileTypeGroup,
} from "@/lib/utils/fileUtils";

interface FileListProps {
	files: FileItem[];
	selectedFiles: string[];
	onSelectionChange: (fileId: string, selected: boolean) => void;
	onPreview: (file: FileItem) => void;
	onDownload: (file: FileItem) => void;
	onShare: (file: FileItem) => void;
	onDelete: (file: FileItem) => void;
	loading?: boolean;
}

// Get file size utility (placeholder since size is not in FileItem)
const getFileSize = (_file: FileItem): number => {
	// Since the FileItem doesn't include size, we'll return 0
	// In a real implementation, this would come from the API
	return 0;
};

const formatDate = (dateString: string): string => {
	if (dateString === "Unknown") return dateString;

	try {
		return new Date(dateString).toLocaleDateString("en-US", {
			year: "numeric",
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		});
	} catch {
		return "Invalid date";
	}
};

const getStatusBadgeClass = (status: string) => {
	switch (status) {
		case "completed":
		case "uploaded":
			return "bg-success/10 text-success-foreground border-success";
		case "processing":
			return "bg-warning/10 text-warning-foreground border-warning";
		case "failed":
		case "error":
			return "bg-destructive/10 text-destructive-foreground border-destructive";
		default:
			return "bg-muted text-muted-foreground border-border";
	}
};

export const FileList: React.FC<FileListProps> = ({
	files,
	selectedFiles,
	onSelectionChange,
	onPreview,
	onDownload,
	onShare,
	onDelete,
	loading = false,
}) => {
	if (loading) {
		return (
			<div className="space-y-2 p-4">
				{Array.from({ length: 8 }).map((_, index) => (
					<div
						key={index}
						className="flex items-center space-x-4 p-3 bg-background border border-border rounded-lg animate-pulse"
					>
						<div className="h-4 w-4 bg-muted rounded" />
						<div className="h-5 w-5 bg-muted rounded" />
						<div className="flex-1 space-y-2">
							<div className="h-4 bg-muted rounded w-1/3" />
							<div className="h-3 bg-muted rounded w-1/2" />
						</div>
						<div className="h-6 w-16 bg-muted rounded-full" />
						<div className="h-8 w-8 bg-muted rounded" />
					</div>
				))}
			</div>
		);
	}

	if (files.length === 0) {
		return (
			<div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
				<FileText className="h-12 w-12 mb-4 text-muted" />
				<p className="text-lg font-medium mb-2">No files found</p>
				<p className="text-sm">Try adjusting your search or filters</p>
			</div>
		);
	}

	return (
		<div className="space-y-2 p-4">
			{files.map((file) => {
				const isSelected = selectedFiles.includes(file.filename);

				return (
					<div
						key={file.filename}
						className={cn(
							"flex items-center space-x-4 p-3 bg-background border border-border rounded-lg hover:shadow-sm transition-shadow cursor-pointer group",
							isSelected && "ring-2 ring-info border-info",
						)}
						onClick={() => onPreview(file)}
					>
						{/* Selection checkbox */}
						<input
							type="checkbox"
							checked={isSelected}
							onChange={(e) => {
								e.stopPropagation();
								onSelectionChange(file.filename, e.target.checked);
							}}
							className="rounded border-border text-info focus:ring-info"
							aria-label={`Select ${file.filename}`}
						/>

						{/* File icon */}
						<div className="flex-shrink-0">
							<FileText className="h-5 w-5 text-muted" />
						</div>

						{/* File details */}
						<div className="flex-1 min-w-0">
							<div className="flex items-center justify-between">
								<h3
									className="text-sm font-medium text-foreground truncate"
									title={file.filename}
								>
									{file.filename}
								</h3>
								<div className="ml-4 text-xs text-muted-foreground">
									{formatFileSizeUtil(getFileSize(file))}
								</div>
							</div>
							<div className="flex items-center justify-between mt-1">
								<p className="text-xs text-muted-foreground">
									{getFileTypeGroup(file.filename).toUpperCase()} •{" "}
									{formatDate(file.createdAt || "Unknown")}
								</p>
							</div>
						</div>

						{/* Status badge */}
						<div className="flex-shrink-0">
							<span
								className={cn(
									"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
									getStatusBadgeClass(file.status || "unknown"),
								)}
							>
								{file.status || "Unknown"}
							</span>
						</div>

						{/* Actions menu */}
						<div className="flex-shrink-0 relative opacity-0 group-hover:opacity-100 transition-opacity">
							<Button
								variant="ghost"
								size="sm"
								className="h-8 w-8 p-0"
								onClick={(e) => {
									e.stopPropagation();
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
										onClick={(e) => {
											e.stopPropagation();
											onPreview(file);
										}}
									>
										<Eye className="mr-2 h-4 w-4" />
										Preview
									</Button>
									<Button
										variant="ghost"
										size="sm"
										className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted justify-start"
										onClick={(e) => {
											e.stopPropagation();
											onDownload(file);
										}}
									>
										<Download className="mr-2 h-4 w-4" />
										Download
									</Button>
									<Button
										variant="ghost"
										size="sm"
										className="flex items-center w-full px-4 py-2 text-sm text-muted-foreground hover:bg-muted justify-start"
										onClick={(e) => {
											e.stopPropagation();
											onShare(file);
										}}
									>
										<Share2 className="mr-2 h-4 w-4" />
										Share
									</Button>
									<Button
										variant="ghost"
										size="sm"
										className="flex items-center w-full px-4 py-2 text-sm text-destructive hover:bg-muted justify-start"
										onClick={(e) => {
											e.stopPropagation();
											onDelete(file);
										}}
									>
										<Trash2 className="mr-2 h-4 w-4" />
										Delete
									</Button>
								</div>
							</div>
						</div>
					</div>
				);
			})}
		</div>
	);
};
