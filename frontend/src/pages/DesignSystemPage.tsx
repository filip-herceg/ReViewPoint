/**
 * Design System Demo Page
 *
 * Showcases all UI components and design tokens from Phase 2.4
 * This page serves as both a functional example and a visual style guide
 */

import {
	BarChart3,
	FileText,
	Layers,
	Palette,
	Upload,
	Users,
} from "lucide-react";
import { useState } from "react";
import { StatusBadge } from "@/components/feedback/StatusBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import { EmptyState } from "@/components/ui/empty-state";
import { FileUpload } from "@/components/ui/file-upload";
import { FormField } from "@/components/ui/form-field";
import { Modal } from "@/components/ui/modal";
import { SkeletonLoader } from "@/components/ui/skeleton-loader";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { useUIStore } from "@/lib/store/uiStore";
import { spacing } from "@/lib/theme/spacing";
import { useTheme } from "@/lib/theme/theme-provider";
import logger from "@/logger";

// Sample data for DataTable demo
const sampleData = [
	{
		id: "1",
		name: "Project Alpha",
		status: "active",
		priority: "high",
		created: "2024-01-15",
	},
	{
		id: "2",
		name: "Beta Release",
		status: "pending",
		priority: "medium",
		created: "2024-01-14",
	},
	{
		id: "3",
		name: "Gamma Testing",
		status: "completed",
		priority: "low",
		created: "2024-01-13",
	},
];

const columns = [
	{ accessorKey: "name", title: "Name", sortable: true },
	{ accessorKey: "status", title: "Status", sortable: true },
	{ accessorKey: "priority", title: "Priority", sortable: true },
	{ accessorKey: "created", title: "Created", sortable: true },
];

export default function DesignSystemPage() {
	const [isModalOpen, setIsModalOpen] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [_formData, setFormData] = useState({
		name: "",
		email: "",
		type: "",
		description: "",
	});

	const { addNotification } = useUIStore();
	const { mode, toggleMode } = useTheme();

	const handleShowNotification = (
		type: "success" | "error" | "warning" | "info",
	) => {
		logger.info(`Showing ${type} notification demo`);
		addNotification({
			type,
			title: `${type.charAt(0).toUpperCase() + type.slice(1)} Demo`,
			message: `This is a sample ${type} notification to demonstrate the toast system.`,
			duration: 3000,
		});
	};

	const handleFileUpload = async (files: File[]) => {
		logger.info("Demo file upload started", { fileCount: files.length });
		setIsLoading(true);

		// Simulate upload process
		await new Promise((resolve) => setTimeout(resolve, 2000));

		setIsLoading(false);
		addNotification({
			type: "success",
			title: "Upload Complete",
			message: `Successfully uploaded ${files.length} file(s)`,
			duration: 3000,
		});
	};

	const _handleFormSubmit = (data: {
		name: string;
		email: string;
		type: string;
		description: string;
	}) => {
		logger.info("Demo form submitted", data);
		setFormData(data);
		addNotification({
			type: "success",
			title: "Form Submitted",
			message: "Form data has been processed successfully",
			duration: 3000,
		});
	};

	return (
		<div className="space-y-8 p-6 bg-background text-foreground">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-4xl font-bold bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
						Design System Demo
					</h1>
					<p className="text-lg text-muted-foreground mt-2">
						Comprehensive showcase of ReViewPoint's UI components and design
						tokens
					</p>
				</div>
				<div className="flex items-center gap-4">
					<ThemeToggle />
					<Badge variant="outline">Phase 2.4</Badge>
				</div>
			</div>

			{/* Design Tokens Overview */}
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<Palette className="h-5 w-5" />
						Design Tokens
					</CardTitle>
					<CardDescription>
						Core design system tokens for consistent theming
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-6">
					{/* Theme Mode */}
					<div>
						<h4 className="text-lg font-semibold">Current Theme</h4>
						<div className="flex items-center gap-4 mt-2">
							<Badge variant={mode === "light" ? "default" : "secondary"}>
								{mode} mode
							</Badge>
							<Button onClick={toggleMode} variant="outline" size="sm">
								Toggle Theme
							</Button>
						</div>
					</div>

					{/* Typography Scale */}
					<div>
						<h4 className="text-lg font-semibold">Typography</h4>
						<div className="space-y-2 mt-2">
							<p className="text-4xl font-bold">Heading 1 - Large Title</p>
							<p className="text-3xl font-bold">Heading 2 - Section Title</p>
							<p className="text-2xl font-semibold">Heading 3 - Subsection</p>
							<p className="text-lg">Large Body Text</p>
							<p className="text-base">Base Body Text</p>
							<p className="text-sm">Small Text</p>
						</div>
					</div>

					{/* Spacing Examples */}
					<div>
						<h4 className="text-lg font-semibold">Spacing Scale</h4>
						<div className="flex flex-wrap gap-2 mt-2">
							{Object.entries(spacing)
								.slice(0, 8)
								.map(([key, value]) => (
									<div key={key} className="flex flex-col items-center">
										<div
											className="bg-primary/20 border border-primary rounded"
											style={{
												width: value,
												height: value,
												minWidth: "8px",
												minHeight: "8px",
											}}
										/>
										<span className="text-xs mt-1 text-muted-foreground">
											{key}
										</span>
									</div>
								))}
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Status Badges */}
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<Layers className="h-5 w-5" />
						Status Components
					</CardTitle>
					<CardDescription>
						Status indicators and badges for different states
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="flex flex-wrap gap-3">
						<StatusBadge status="success" />
						<StatusBadge status="error" />
						<StatusBadge status="warning" />
						<StatusBadge status="info" />
						<StatusBadge status="pending" />
						<StatusBadge status="completed" />
						<StatusBadge status="failed" />
					</div>
				</CardContent>
			</Card>

			{/* Interactive Components */}
			<div className="grid lg:grid-cols-2 gap-6">
				{/* Buttons and Actions */}
				<Card>
					<CardHeader>
						<CardTitle>Interactive Elements</CardTitle>
						<CardDescription>
							Buttons, notifications, and user actions
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-4">
						<div className="flex flex-wrap gap-2">
							<Button onClick={() => handleShowNotification("success")}>
								Success Toast
							</Button>
							<Button
								onClick={() => handleShowNotification("error")}
								variant="destructive"
							>
								Error Toast
							</Button>
							<Button
								onClick={() => handleShowNotification("warning")}
								variant="outline"
							>
								Warning Toast
							</Button>
							<Button
								onClick={() => handleShowNotification("info")}
								variant="secondary"
							>
								Info Toast
							</Button>
						</div>

						<div className="flex flex-wrap gap-2">
							<Button onClick={() => setIsModalOpen(true)}>Open Modal</Button>
							<Button
								onClick={() => setIsLoading(!isLoading)}
								variant="outline"
								disabled={isLoading}
							>
								{isLoading ? "Loading..." : "Toggle Loading"}
							</Button>
						</div>
					</CardContent>
				</Card>

				{/* Form Components */}
				<Card>
					<CardHeader>
						<CardTitle>Form Components</CardTitle>
						<CardDescription>
							Robust form fields with validation
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-4">
						<FormField
							name="demo-name"
							label="Project Name"
							type="text"
							placeholder="Enter project name"
							required
						/>
						<FormField
							name="demo-email"
							label="Contact Email"
							type="email"
							placeholder="contact@example.com"
							required
						/>
						<FormField
							name="demo-description"
							label="Description"
							type="textarea"
							placeholder="Describe your project..."
						/>
						<Button onClick={() => handleShowNotification("success")}>
							Submit Demo Form
						</Button>
					</CardContent>
				</Card>
			</div>

			{/* File Upload Demo */}
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<Upload className="h-5 w-5" />
						File Upload Component
					</CardTitle>
					<CardDescription>
						Drag-and-drop file upload with validation and progress
					</CardDescription>
				</CardHeader>
				<CardContent>
					<FileUpload
						onFilesSelected={handleFileUpload}
						validation={{
							maxSize: 10 * 1024 * 1024, // 10MB
							maxFiles: 5,
							allowedTypes: [".pdf", ".doc", ".docx", ".txt"],
						}}
						disabled={isLoading}
						multiple
					/>
				</CardContent>
			</Card>

			{/* Data Table Demo */}
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<BarChart3 className="h-5 w-5" />
						Data Table Component
					</CardTitle>
					<CardDescription>
						Advanced data table with sorting, filtering, and pagination
					</CardDescription>
				</CardHeader>
				<CardContent>
					<DataTable
						data={sampleData}
						columns={columns.map((col) => ({ ...col, key: col.accessorKey }))}
						loading={isLoading}
						emptyMessage="No projects found"
					/>
				</CardContent>
			</Card>

			{/* Loading States */}
			<Card>
				<CardHeader>
					<CardTitle>Loading States</CardTitle>
					<CardDescription>
						Various skeleton loaders for different content types
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="grid md:grid-cols-2 gap-4">
						<div>
							<h5 className="text-base font-semibold">Card Skeleton</h5>
							<SkeletonLoader variant="card" className="mt-2" />
						</div>
						<div>
							<h5 className="text-base font-semibold">List Skeleton</h5>
							<SkeletonLoader variant="list" className="mt-2" />
						</div>
						<div>
							<h5 className="text-base font-semibold">Text Skeleton</h5>
							<SkeletonLoader variant="text" className="mt-2" />
						</div>
						<div>
							<h5 className="text-base font-semibold">Circular Skeleton</h5>
							<SkeletonLoader variant="circular" className="mt-2" />
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Empty States */}
			<Card>
				<CardHeader>
					<CardTitle>Empty State Components</CardTitle>
					<CardDescription>
						Consistent empty states for different scenarios
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="grid md:grid-cols-2 gap-6">
						<EmptyState
							icon={<FileText className="h-12 w-12" />}
							title="No Documents"
							description="Upload your first document to get started"
							action={{
								label: "Upload Document",
								onClick: () => handleShowNotification("info"),
							}}
						/>
						<EmptyState
							icon={<Users className="h-12 w-12" />}
							title="No Team Members"
							description="Invite colleagues to collaborate on projects"
							action={{
								label: "Invite Members",
								onClick: () => handleShowNotification("info"),
							}}
						/>
					</div>
				</CardContent>
			</Card>

			{/* Modal Demo */}
			<Modal
				open={isModalOpen}
				onOpenChange={setIsModalOpen}
				title="Demo Modal"
				size="md"
			>
				<div className="space-y-4">
					<p>
						This is a demonstration of the modal component with our design
						system.
					</p>
					<div className="flex justify-end gap-2">
						<Button variant="outline" onClick={() => setIsModalOpen(false)}>
							Cancel
						</Button>
						<Button
							onClick={() => {
								setIsModalOpen(false);
								handleShowNotification("success");
							}}
						>
							Confirm
						</Button>
					</div>
				</div>
			</Modal>

			{/* Footer */}
			<div className="text-center py-8 border-t border-border bg-background">
				<p className="text-sm text-muted-foreground">
					Design System Demo - ReViewPoint Phase 2.4
				</p>
			</div>
		</div>
	);
}
