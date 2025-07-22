import {
	Filter,
	Grid,
	List,
	RefreshCw,
	Search,
	SortAsc,
	SortDesc,
	Table,
} from "lucide-react";
import type React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export type ViewMode = "table" | "grid" | "list";
export type SortField = "filename" | "size" | "created_at" | "content_type";
export type SortOrder = "asc" | "desc";

interface FileToolbarProps {
	searchQuery: string;
	onSearchChange: (query: string) => void;
	viewMode: ViewMode;
	onViewModeChange: (mode: ViewMode) => void;
	sortField: SortField;
	sortOrder: SortOrder;
	onSortChange: (field: SortField, order: SortOrder) => void;
	onRefresh: () => void;
	onShowFilters: () => void;
	totalFiles: number;
	selectedCount: number;
	isRefreshing?: boolean;
}

export const FileToolbar: React.FC<FileToolbarProps> = ({
	searchQuery,
	onSearchChange,
	viewMode,
	onViewModeChange,
	sortField,
	sortOrder,
	onSortChange,
	onRefresh,
	onShowFilters,
	totalFiles,
	selectedCount,
	isRefreshing = false,
}) => {
	const handleSortClick = (field: SortField) => {
		if (sortField === field) {
			// Toggle order if same field
			onSortChange(field, sortOrder === "asc" ? "desc" : "asc");
		} else {
			// Default to ascending for new field
			onSortChange(field, "asc");
		}
	};

	return (
		<div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between p-4 bg-background border-b border-border">
			{/* Left section - Search and filters */}
			<div className="flex flex-1 items-center gap-2 min-w-0">
				<div className="relative flex-1 max-w-sm">
					<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted" />
					<Input
						type="text"
						placeholder="Search files..."
						value={searchQuery}
						onChange={(e) => onSearchChange(e.target.value)}
						className="pl-9"
						role="searchbox"
						aria-label="Search files"
					/>
				</div>{" "}
				<Button
					variant="outline"
					size="sm"
					onClick={onShowFilters}
					className="whitespace-nowrap"
					aria-label="Open filters"
				>
					<Filter className="h-4 w-4 mr-2" />
					Filters
				</Button>
			</div>

			{/* Center section - File count and selection info */}
			<div className="flex items-center gap-4 text-sm text-muted-foreground">
				<span>
					{totalFiles} file{totalFiles !== 1 ? "s" : ""}
					{selectedCount > 0 && (
						<span className="ml-2 px-2 py-1 bg-info/10 text-info-foreground rounded-full text-xs border border-info">
							{selectedCount} selected
						</span>
					)}
				</span>
			</div>

			{/* Right section - Sort, view controls, and refresh */}
			<div className="flex items-center gap-2">
				{/* Sort dropdown */}
				<div className="relative">
					<Button
						variant="outline"
						size="sm"
						onClick={(e) => {
							e.preventDefault();
							const menu = e.currentTarget.nextElementSibling as HTMLElement;
							if (menu) {
								menu.classList.toggle("hidden");
							}
						}}
						className="whitespace-nowrap"
						aria-label="Sort by"
						aria-expanded="false"
						aria-haspopup="listbox"
					>
						{sortOrder === "asc" ? (
							<SortAsc className="h-4 w-4 mr-2" />
						) : (
							<SortDesc className="h-4 w-4 mr-2" />
						)}
						Sort
					</Button>
					<div className="hidden absolute right-0 mt-2 w-48 bg-background rounded-md shadow-lg border border-border z-10">
						<div className="py-1">
							{[
								{ field: "filename" as SortField, label: "Name" },
								{ field: "size" as SortField, label: "Size" },
								{ field: "created_at" as SortField, label: "Date" },
								{ field: "content_type" as SortField, label: "Type" },
							].map(({ field, label }) => (
								<Button
									key={field}
									variant="ghost"
									size="sm"
									className={cn(
										"flex items-center w-full px-4 py-2 text-sm hover:bg-muted justify-between",
										sortField === field
											? "text-info bg-info/10"
											: "text-foreground",
									)}
									onClick={() => handleSortClick(field)}
									aria-selected={sortField === field}
								>
									<span className="flex-1 text-left">{label}</span>
									{sortField === field &&
										(sortOrder === "asc" ? (
											<SortAsc className="h-4 w-4" />
										) : (
											<SortDesc className="h-4 w-4" />
										))}
								</Button>
							))}
						</div>
					</div>
				</div>

				{/* View mode toggle */}
				<div className="flex items-center border border-border rounded-md">
					<Button
						variant={viewMode === "table" ? "default" : "ghost"}
						size="sm"
						onClick={() => onViewModeChange("table")}
						className="rounded-r-none border-r border-border"
					>
						<Table className="h-4 w-4" />
						<span className="sr-only">Table view</span>
					</Button>
					<Button
						variant={viewMode === "grid" ? "default" : "ghost"}
						size="sm"
						onClick={() => onViewModeChange("grid")}
						className="rounded-none border-r border-border"
					>
						<Grid className="h-4 w-4" />
						<span className="sr-only">Grid view</span>
					</Button>
					<Button
						variant={viewMode === "list" ? "default" : "ghost"}
						size="sm"
						onClick={() => onViewModeChange("list")}
						className="rounded-l-none"
					>
						<List className="h-4 w-4" />
						<span className="sr-only">List view</span>
					</Button>
				</div>

				{/* Refresh button */}
				<Button
					variant="outline"
					size="sm"
					onClick={onRefresh}
					disabled={isRefreshing}
					className="whitespace-nowrap"
				>
					<RefreshCw
						className={cn("h-4 w-4", isRefreshing && "animate-spin")}
					/>
					<span className="sr-only">Refresh</span>
				</Button>
			</div>
		</div>
	);
};
