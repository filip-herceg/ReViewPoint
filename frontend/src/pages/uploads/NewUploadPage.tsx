import { AlertCircle, ArrowLeft, CheckCircle2, Upload, X } from "lucide-react";
import type React from "react";
import { useCallback, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
// import { Label } from '@/components/ui/label';
// import { Textarea } from '@/components/ui/textarea';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const NewUploadPage: React.FC = () => {
	const navigate = useNavigate();
	const [isUploading, setIsUploading] = useState(false);
	const [uploadProgress, setUploadProgress] = useState(0);
	const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
	const [formData, setFormData] = useState({
		title: "",
		description: "",
		tags: [] as string[],
		tagInput: "",
	});

	const handleFileSelect = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>) => {
			const files = Array.from(event.target.files || []);
			setSelectedFiles((prev) => [...prev, ...files]);
		},
		[],
	);

	const handleFileDrop = useCallback(
		(event: React.DragEvent<HTMLDivElement>) => {
			event.preventDefault();
			const files = Array.from(event.dataTransfer.files);
			setSelectedFiles((prev) => [...prev, ...files]);
		},
		[],
	);

	const handleDragOver = useCallback(
		(event: React.DragEvent<HTMLDivElement>) => {
			event.preventDefault();
		},
		[],
	);

	const removeFile = (index: number) => {
		setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
	};

	const addTag = () => {
		const tag = formData.tagInput.trim().toLowerCase();
		if (tag && !formData.tags.includes(tag)) {
			setFormData((prev) => ({
				...prev,
				tags: [...prev.tags, tag],
				tagInput: "",
			}));
		}
	};

	const removeTag = (tagToRemove: string) => {
		setFormData((prev) => ({
			...prev,
			tags: prev.tags.filter((tag) => tag !== tagToRemove),
		}));
	};

	const handleTagInputKeyDown = (event: React.KeyboardEvent) => {
		if (event.key === "Enter") {
			event.preventDefault();
			addTag();
		}
	};

	const formatFileSize = (bytes: number) => {
		if (bytes === 0) return "0 Bytes";
		const k = 1024;
		const sizes = ["Bytes", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return `${parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`;
	};

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();

		if (selectedFiles.length === 0) {
			alert("Please select at least one file to upload.");
			return;
		}

		setIsUploading(true);
		setUploadProgress(0);

		try {
			// TODO: Replace with actual API call
			// Simulate upload progress
			for (let i = 0; i <= 100; i += 10) {
				setUploadProgress(i);
				await new Promise((resolve) => setTimeout(resolve, 100));
			}

			// Simulate successful upload
			setTimeout(() => {
				navigate("/uploads");
			}, 1000);
		} catch (error) {
			console.error("Upload failed:", error);
			setIsUploading(false);
			alert("Upload failed. Please try again.");
		}
	};

	const getTotalSize = () => {
		return selectedFiles.reduce((total, file) => total + file.size, 0);
	};

	const getFileIcon = (file: File) => {
		if (file.type.startsWith("image/")) return "🖼️";
		if (file.type.includes("pdf")) return "📄";
		if (file.type.includes("word")) return "📝";
		if (file.type.includes("excel") || file.type.includes("spreadsheet"))
			return "📊";
		if (file.type.includes("powerpoint") || file.type.includes("presentation"))
			return "📊";
		if (file.type.startsWith("text/")) return "📄";
		return "📎";
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-accent/10">
			<div className="container mx-auto px-6 py-8 space-y-8">
				{/* Header */}
				<div className="flex items-center gap-4">
					<Button variant="ghost" size="sm" asChild className="hover-lift">
						<Link to="/uploads">
							<span className="flex items-center">
								<ArrowLeft className="h-4 w-4 mr-2" />
								<span>Back to Uploads</span>
							</span>
						</Link>
					</Button>
				</div>

				<div className="text-center space-y-4">
					<h1 className="text-4xl font-bold bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
						Upload Document
					</h1>
					<p className="text-body-lg text-muted-foreground max-w-2xl mx-auto">
						Upload documents for review and collaboration with your team.
					</p>
				</div>

				<form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-8">
					{/* File Upload */}
					<Card className="glass-card">
						<CardHeader>
							<CardTitle className="text-xl font-semibold">
								Select Files
							</CardTitle>
							<CardDescription>
								Drag and drop files here or click to browse. Supported formats:
								PDF, DOC, DOCX, TXT, MD, and more.
							</CardDescription>
						</CardHeader>
						<CardContent>
							<div
								className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center hover:border-muted-foreground/50 transition-colors"
								onDrop={handleFileDrop}
								onDragOver={handleDragOver}
							>
								<Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
								<div className="space-y-2">
									<p className="text-lg font-medium">
										Drop files here or click to upload
									</p>
									<p className="text-sm text-muted-foreground">
										Maximum file size: 50MB per file
									</p>
								</div>
								<input
									type="file"
									multiple
									onChange={handleFileSelect}
									className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
									accept=".pdf,.doc,.docx,.txt,.md,.rtf"
									disabled={isUploading}
								/>
							</div>

							{/* Selected Files */}
							{selectedFiles.length > 0 && (
								<div className="mt-6 space-y-3">
									<div className="flex items-center justify-between">
										<h4 className="font-medium">
											Selected Files ({selectedFiles.length})
										</h4>
										<p className="text-sm text-muted-foreground">
											Total size: {formatFileSize(getTotalSize())}
										</p>
									</div>
									<div className="space-y-2 max-h-48 overflow-y-auto">
										{selectedFiles.map((file, index) => (
											<div
												key={index}
												className="flex items-center justify-between p-3 border rounded-lg"
											>
												<div className="flex items-center gap-3">
													<span className="text-lg">{getFileIcon(file)}</span>
													<div>
														<p className="font-medium text-sm">{file.name}</p>
														<p className="text-xs text-muted-foreground">
															{formatFileSize(file.size)} •{" "}
															{file.type || "Unknown type"}
														</p>
													</div>
												</div>
												<Button
													type="button"
													variant="ghost"
													size="sm"
													onClick={() => removeFile(index)}
													disabled={isUploading}
												>
													<X className="h-4 w-4" />
												</Button>
											</div>
										))}
									</div>
								</div>
							)}
						</CardContent>
					</Card>

					{/* Document Details */}
					<Card>
						<CardHeader>
							<CardTitle>Document Details</CardTitle>
							<CardDescription>
								Provide additional information about your upload to help
								reviewers understand the context.
							</CardDescription>
						</CardHeader>
						<CardContent className="space-y-4">
							<div className="space-y-2">
								<label htmlFor="title" className="text-sm font-medium">
									Title
								</label>
								<Input
									id="title"
									placeholder="Enter a descriptive title for your upload"
									value={formData.title}
									onChange={(e) =>
										setFormData((prev) => ({ ...prev, title: e.target.value }))
									}
									disabled={isUploading}
									required
								/>
							</div>

							<div className="space-y-2">
								<label htmlFor="description" className="text-sm font-medium">
									Description
								</label>
								<textarea
									id="description"
									placeholder="Provide a detailed description of the document and what reviewers should focus on"
									value={formData.description}
									onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
										setFormData((prev) => ({
											...prev,
											description: e.target.value,
										}))
									}
									disabled={isUploading}
									rows={4}
									className="w-full px-3 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary/50 transition-colors"
								/>
							</div>

							<div className="space-y-2">
								<label htmlFor="tags" className="text-sm font-medium">
									Tags
								</label>
								<div className="flex gap-2">
									<Input
										id="tags"
										placeholder="Add tags to categorize your document"
										value={formData.tagInput}
										onChange={(e) =>
											setFormData((prev) => ({
												...prev,
												tagInput: e.target.value,
											}))
										}
										onKeyDown={handleTagInputKeyDown}
										disabled={isUploading}
									/>
									<Button
										type="button"
										variant="outline"
										onClick={addTag}
										disabled={isUploading}
									>
										Add
									</Button>
								</div>
								{formData.tags.length > 0 && (
									<div className="flex flex-wrap gap-2 mt-2">
										{formData.tags.map((tag) => (
											<Badge
												key={tag}
												variant="secondary"
												className="flex items-center gap-1"
											>
												{tag}
												<Button
													type="button"
													variant="icon-sm"
													size="icon-sm"
													onClick={() => removeTag(tag)}
													disabled={isUploading}
													className="ml-1 hover:text-destructive"
												>
													Remove
												</Button>
											</Badge>
										))}
									</div>
								)}
							</div>
						</CardContent>
					</Card>

					{/* Upload Progress */}
					{isUploading && (
						<Card>
							<CardContent className="pt-6">
								<div className="space-y-4">
									<div className="flex items-center gap-2">
										<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
										<span className="text-sm font-medium">
											Uploading files... {uploadProgress}%
										</span>
									</div>
									<div className="w-full bg-secondary rounded-full h-2">
										<div
											className="bg-primary h-2 rounded-full transition-all duration-300"
											style={{ width: `${uploadProgress}%` }}
										/>
									</div>
								</div>
							</CardContent>
						</Card>
					)}

					{/* Guidelines */}
					<Card>
						<CardHeader>
							<CardTitle className="flex items-center gap-2">
								<AlertCircle className="h-5 w-5" />
								Upload Guidelines
							</CardTitle>
						</CardHeader>
						<CardContent>
							<ul className="space-y-2 text-sm">
								<li className="flex items-start gap-2">
									<CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
									<span>
										Ensure documents are free of sensitive or confidential
										information
									</span>
								</li>
								<li className="flex items-start gap-2">
									<CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
									<span>
										Use descriptive titles and comprehensive descriptions
									</span>
								</li>
								<li className="flex items-start gap-2">
									<CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
									<span>
										Add relevant tags to help reviewers find and categorize your
										documents
									</span>
								</li>
								<li className="flex items-start gap-2">
									<CheckCircle2 className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
									<span>Maximum file size is 50MB per file</span>
								</li>
							</ul>
						</CardContent>
					</Card>

					{/* Submit */}
					<div className="flex items-center gap-4">
						<Button
							type="submit"
							disabled={
								selectedFiles.length === 0 ||
								isUploading ||
								!formData.title.trim()
							}
							className="min-w-32"
						>
							{isUploading ? (
								<>
									<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
									Uploading...
								</>
							) : (
								<>
									<Upload className="h-4 w-4 mr-2" />
									Upload Files
								</>
							)}
						</Button>
						<Button
							type="button"
							variant="outline"
							asChild
							disabled={isUploading}
						>
							<Link to="/uploads" className="flex items-center">
								Cancel
							</Link>
						</Button>
					</div>
				</form>
			</div>
		</div>
	);
};

export default NewUploadPage;
