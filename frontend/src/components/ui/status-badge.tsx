import {
	AlertCircle,
	CheckCircle,
	Clock,
	Eye,
	FileText,
	Pause,
	RefreshCw,
	Upload,
	XCircle,
} from "lucide-react";
import React from "react";
import { Badge } from "@/components/ui/badge";

// Status color mappings
export const getStatusColor = (status: string) => {
	switch (status) {
		case "pending":
			return "bg-warning/10 text-warning";
		case "in-review":
			return "bg-primary text-inverse";
		case "in-progress":
			return "bg-info/10 text-info";
		case "reviewed":
			return "bg-success/10 text-success-foreground";
		case "rejected":
			return "bg-destructive/10 text-destructive";
		case "completed":
			return "bg-success/10 text-success-foreground";
		case "success":
			return "bg-success text-success-foreground";
		case "warning":
			return "bg-warning text-warning-foreground";
		case "error":
			return "bg-destructive text-destructive-foreground";
		case "failed":
			return "bg-destructive text-destructive-foreground";
		case "info":
			return "bg-info text-info-foreground";
		case "uploading":
			return "bg-info/10 text-info";
		case "processing":
			return "bg-info/10 text-info";
		case "paused":
			return "bg-muted text-muted-foreground";
		case "reviewing":
			return "bg-accent/10 text-accent";
		default:
			return "bg-muted text-muted-foreground";
	}
};

// Priority color mappings
export const getPriorityColor = (priority: string) => {
	switch (priority) {
		case "high":
			return "bg-destructive/10 text-destructive";
		case "medium":
			return "bg-warning/10 text-warning";
		case "low":
			return "bg-success/10 text-success-foreground";
		default:
			return "bg-muted text-muted-foreground";
	}
};

// Status icon mappings
export const getStatusIcon = (status: string) => {
	switch (status) {
		case "pending":
			return <Clock className="h-4 w-4" />;
		case "in-review":
			return <Eye className="h-4 w-4" />;
		case "in-progress":
			return <RefreshCw className="h-4 w-4" />;
		case "reviewed":
			return <CheckCircle className="h-4 w-4" />;
		case "completed":
			return <CheckCircle className="h-4 w-4" />;
		case "success":
			return <CheckCircle className="h-4 w-4" />;
		case "rejected":
			return <XCircle className="h-4 w-4" />;
		case "failed":
			return <XCircle className="h-4 w-4" />;
		case "error":
			return <XCircle className="h-4 w-4" />;
		case "warning":
			return <AlertCircle className="h-4 w-4" />;
		case "info":
			return <AlertCircle className="h-4 w-4" />;
		case "uploading":
			return <Upload className="h-4 w-4" />;
		case "processing":
			return <RefreshCw className="h-4 w-4" />;
		case "paused":
			return <Pause className="h-4 w-4" />;
		case "reviewing":
			return <Eye className="h-4 w-4" />;
		default:
			return <FileText className="h-4 w-4" />;
	}
};

// Reusable StatusBadge component
interface StatusBadgeProps {
	status: string;
	showIcon?: boolean;
	className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
	status,
	showIcon = true,
	className = "",
}) => {
	const statusColor = getStatusColor(status);
	const textColor = statusColor.split(" ")[1]; // Extract text color class

	return (
		<Badge className={`${statusColor} ${className}`}>
			{showIcon &&
				React.cloneElement(getStatusIcon(status), {
					className: `h-4 w-4 ${textColor} ${status === "processing" ? "animate-spin" : ""}`,
				})}
			<span className={`${showIcon ? "ml-1" : ""} capitalize ${textColor}`}>
				{status === "in-progress" ? "In Progress" : status}
			</span>
		</Badge>
	);
};

// Reusable PriorityBadge component
interface PriorityBadgeProps {
	priority: string;
	className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
	priority,
	className = "",
}) => {
	const priorityColor = getPriorityColor(priority);
	const textColor = priorityColor.split(" ")[1]; // Extract text color class

	return (
		<Badge className={`${priorityColor} ${className}`}>
			<span className={`capitalize ${textColor}`}>{priority} priority</span>
		</Badge>
	);
};

// Reusable OverdueBadge component
interface OverdueBadgeProps {
	className?: string;
}

export const OverdueBadge: React.FC<OverdueBadgeProps> = ({
	className = "",
}) => {
	const overdueColor = getPriorityColor("high"); // Same color as high priority
	const textColor = overdueColor.split(" ")[1]; // Extract text color class

	return (
		<Badge className={`${overdueColor} ${className}`}>
			<span className={`capitalize ${textColor}`}>Overdue</span>
		</Badge>
	);
};
