/**
 * Moderation Panel Page
 *
 * Content moderation interface for reviewing flagged content and managing
 * community standards. Accessible to users with 'admin' or 'moderator' roles.
 */

import {
	AlertTriangle,
	CheckCircle,
	Eye,
	Flag,
	Shield,
	UserCheck,
	XCircle,
} from "lucide-react";
import { RequireAnyRole, ShowForRoles } from "@/components/auth/AuthGuard";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";

// Mock flagged content data
const mockFlaggedContent = [
	{
		id: 1,
		type: "upload",
		title: "Suspicious File Upload",
		reporter: "user123@example.com",
		reason: "Inappropriate content",
		status: "pending",
		reportedAt: "2025-01-09T10:30:00Z",
		priority: "high",
	},
	{
		id: 2,
		type: "comment",
		title: "Offensive Comment on Review #456",
		reporter: "moderator@example.com",
		reason: "Hate speech",
		status: "under_review",
		reportedAt: "2025-01-08T15:45:00Z",
		priority: "high",
	},
	{
		id: 3,
		type: "upload",
		title: "Potential Copyright Violation",
		reporter: "admin@example.com",
		reason: "Copyright infringement",
		status: "pending",
		reportedAt: "2025-01-08T09:15:00Z",
		priority: "medium",
	},
];

function getPriorityBadge(priority: string) {
	const variants = {
		high: "destructive",
		medium: "default",
		low: "secondary",
	} as const;
	return (
		<Badge variant={variants[priority as keyof typeof variants]}>
			{priority}
		</Badge>
	);
}

function getStatusBadge(status: string) {
	const config = {
		pending: { variant: "secondary", icon: AlertTriangle },
		under_review: { variant: "default", icon: Eye },
		resolved: { variant: "default", icon: CheckCircle },
		dismissed: { variant: "secondary", icon: XCircle },
	} as const;

	const { variant, icon: Icon } =
		config[status as keyof typeof config] || config.pending;

	return (
		<Badge variant={variant as any} className="flex items-center gap-1">
			<Icon className="h-3 w-3" />
			{status.replace("_", " ")}
		</Badge>
	);
}

export default function ModerationPanelPage() {
	return (
		<RequireAnyRole
			roles={["admin", "moderator"]}
			fallback={
				<Alert variant="destructive">
					<Shield className="h-4 w-4" />
					<AlertDescription>
						You need administrator or moderator privileges to access this page.
					</AlertDescription>
				</Alert>
			}
		>
			<div className="space-y-6">
				{/* Page Header */}
				<div className="border-b border-border pb-4">
					<h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
						<UserCheck className="h-8 w-8" />
						Moderation Panel
					</h1>
					<p className="text-muted-foreground mt-2">
						Review flagged content and manage community standards
					</p>
				</div>

				{/* Moderation Statistics */}
				<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
					<Card>
						<CardContent className="p-4">
							<div className="text-2xl font-bold text-destructive">
								{
									mockFlaggedContent.filter((item) => item.status === "pending")
										.length
								}
							</div>
							<div className="text-sm text-muted-foreground">
								Pending Review
							</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent className="p-4">
							<div className="text-2xl font-bold text-warning-foreground">
								{
									mockFlaggedContent.filter(
										(item) => item.status === "under_review",
									).length
								}
							</div>
							<div className="text-sm text-muted-foreground">Under Review</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent className="p-4">
							<div className="text-2xl font-bold text-destructive">
								{
									mockFlaggedContent.filter((item) => item.priority === "high")
										.length
								}
							</div>
							<div className="text-sm text-muted-foreground">High Priority</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent className="p-4">
							<div className="text-2xl font-bold text-primary">
								{mockFlaggedContent.length}
							</div>
							<div className="text-sm text-muted-foreground">Total Reports</div>
						</CardContent>
					</Card>
				</div>

				{/* Admin-only Section */}
				<ShowForRoles roles={["admin"]}>
					<Alert>
						<Shield className="h-4 w-4" />
						<AlertDescription>
							<strong>Admin Only:</strong> You have full moderation privileges
							including the ability to permanently ban users and delete content.
						</AlertDescription>
					</Alert>
				</ShowForRoles>

				{/* Flagged Content */}
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<Flag className="h-5 w-5" />
							Flagged Content
						</CardTitle>
						<CardDescription>
							Review and take action on reported content
						</CardDescription>
					</CardHeader>
					<CardContent>
						<div className="space-y-4">
							{mockFlaggedContent.map((item) => (
								<div
									key={item.id}
									className="border border-border rounded-lg p-4 hover:bg-muted/50"
								>
									<div className="flex items-start justify-between">
										<div className="flex-1">
											<div className="flex items-center gap-2 mb-2">
												<h3 className="font-medium text-foreground">
													{item.title}
												</h3>
												{getPriorityBadge(item.priority)}
												{getStatusBadge(item.status)}
											</div>
											<div className="text-sm text-muted-foreground space-y-1">
												<div>
													<strong>Type:</strong> {item.type}
												</div>
												<div>
													<strong>Reason:</strong> {item.reason}
												</div>
												<div>
													<strong>Reporter:</strong> {item.reporter}
												</div>
												<div>
													<strong>Reported:</strong>{" "}
													{new Date(item.reportedAt).toLocaleString()}
												</div>
											</div>
										</div>
										<div className="flex gap-2 ml-4">
											<Button variant="outline" size="sm">
												<Eye className="h-4 w-4 mr-1" />
												Review
											</Button>
											<Button variant="outline-success" size="sm">
												<CheckCircle className="h-4 w-4 mr-1" />
												Approve
											</Button>
											<Button variant="outline-destructive" size="sm">
												<XCircle className="h-4 w-4 mr-1" />
												Remove
											</Button>
										</div>
									</div>
								</div>
							))}
						</div>
					</CardContent>
				</Card>

				{/* Quick Actions for Moderators */}
				<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
					<Card>
						<CardHeader>
							<CardTitle>Quick Actions</CardTitle>
							<CardDescription>Common moderation tasks</CardDescription>
						</CardHeader>
						<CardContent className="space-y-3">
							<Button variant="outline" className="w-full justify-start">
								<Flag className="h-4 w-4 mr-2" />
								Review All Pending Reports
							</Button>
							<Button variant="outline" className="w-full justify-start">
								<UserCheck className="h-4 w-4 mr-2" />
								View User Activity Logs
							</Button>
							<Button variant="outline" className="w-full justify-start">
								<Shield className="h-4 w-4 mr-2" />
								Update Community Guidelines
							</Button>
						</CardContent>
					</Card>

					<Card>
						<CardHeader>
							<CardTitle>Moderation Guidelines</CardTitle>
							<CardDescription>
								Quick reference for content review
							</CardDescription>
						</CardHeader>
						<CardContent>
							<div className="space-y-2 text-sm text-muted-foreground">
								<div>• Review content within 24 hours of reporting</div>
								<div>• Document all actions taken</div>
								<div>• Escalate sensitive cases to administrators</div>
								<div>• Follow community guidelines consistently</div>
								<div>• Provide clear feedback to users when possible</div>
							</div>
						</CardContent>
					</Card>
				</div>
			</div>
		</RequireAnyRole>
	);
}
