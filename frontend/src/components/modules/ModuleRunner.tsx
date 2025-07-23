/**
 * Module Runner Component - Allows users to run modules on documents
 * Integrated into document detail pages for easy module execution
 */

import {
	AlertTriangle,
	Award,
	BookCheck,
	CheckCircle,
	Clock,
	Play,
	Settings,
	Shield,
	Target,
} from "lucide-react";
import type React from "react";
import { useState } from "react";
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
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useMarketplace } from "@/hooks/useMarketplace";
import type { Module, ModuleExecutionResult } from "@/types/marketplace";

// Mock result interfaces for simulation
interface MockResultDetails {
	totalCitations?: number;
	validCitations?: number;
	invalidCitations?: number;
	missingInfo?: number;
	formatIssues?: number;
	duplicateCount?: number;
	uniqueCount?: number;
	sentimentScore?: number;
	biasScore?: number;
	totalIssues?: number;
	criticalIssues?: number;
	grammar?: number;
	spelling?: number;
	style?: number;
	integrity?: number;
	transparency?: number;
	overallSimilarity?: number;
	structureScore?: number;
	suspiciousSegments?: number;
	methodologyScore?: number;
	checkedSources?: number;
	clarityScore?: number;
	evidenceScore?: number;
}

interface MockResult {
	summary: string;
	details: MockResultDetails;
	confidence: number;
	suggestions: string[];
	warnings: string[];
	errors: string[];
}

interface ModuleRunnerProps {
	documentId: string;
	documentName: string;
	documentType?: string;
	compact?: boolean;
}

// Mock execution function (would be replaced with real API call)
const mockExecuteModule = async (
	moduleId: string,
	documentId: string,
): Promise<ModuleExecutionResult> => {
	// Simulate processing time
	await new Promise((resolve) =>
		setTimeout(resolve, 2000 + Math.random() * 3000),
	);

	// Mock results based on module type
	const mockResults: Record<string, MockResult> = {
		"citation-validator-pro": {
			summary: "Found 12 citations, 2 require attention",
			details: {
				totalCitations: 12,
				validCitations: 10,
				invalidCitations: 2,
				missingInfo: 1,
				formatIssues: 1,
			},
			confidence: 0.92,
			suggestions: [
				"Update citation #3 to include page numbers",
				"Verify publication date for citation #7",
			],
			warnings: ["Citation #3 missing page numbers"],
			errors: [],
		},
		"plagiarism-detector": {
			summary: "No significant plagiarism detected",
			details: {
				overallSimilarity: 8.5,
				suspiciousSegments: 0,
				checkedSources: 45000000,
			},
			confidence: 0.96,
			suggestions: ["Consider adding more original analysis in section 3"],
			warnings: [],
			errors: [],
		},
		"quality-assessor": {
			summary: "Overall quality score: 87/100",
			details: {
				structureScore: 92,
				methodologyScore: 85,
				clarityScore: 84,
				evidenceScore: 89,
			},
			confidence: 0.89,
			suggestions: [
				"Improve methodology description in section 2",
				"Add more transitional phrases for better flow",
				"Consider strengthening the conclusion",
			],
			warnings: ["Some technical terms could benefit from definitions"],
			errors: [],
		},
	};

	const result = mockResults[moduleId] || {
		summary: "Analysis completed successfully",
		details: { processed: true },
		confidence: 0.85,
		suggestions: ["No specific suggestions available"],
		warnings: [],
		errors: [],
	};

	return {
		moduleId,
		executionId: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
		documentId,
		startTime: new Date(Date.now() - 3000).toISOString(),
		endTime: new Date().toISOString(),
		status: Math.random() > 0.1 ? "success" : "warning", // 90% success rate
		results: result,
		processedPages: Math.floor(Math.random() * 20) + 5,
		totalPages: Math.floor(Math.random() * 25) + 10,
	};
};

const getModuleIcon = (category: string) => {
	switch (category) {
		case "citation":
			return BookCheck;
		case "analysis":
			return Shield;
		case "quality":
			return Award;
		default:
			return Target;
	}
};

const getStatusColor = (status: string) => {
	switch (status) {
		case "success":
			return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
		case "warning":
			return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
		case "error":
			return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
		default:
			return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
	}
};

const ModuleRunner: React.FC<ModuleRunnerProps> = ({
	documentId,
	documentName: _documentName,
	documentType: _documentType,
	compact = false,
}) => {
	const { userSubscriptions } = useMarketplace();
	const [runningModules, setRunningModules] = useState<Set<string>>(new Set());
	const [results, setResults] = useState<Record<string, ModuleExecutionResult>>(
		{},
	);

	const executeModule = async (module: Module) => {
		setRunningModules((prev) => new Set(prev).add(module.id));

		try {
			const result = await mockExecuteModule(module.id, documentId);
			setResults((prev) => ({ ...prev, [module.id]: result }));
		} catch (error) {
			console.error("Module execution failed:", error);
		} finally {
			setRunningModules((prev) => {
				const next = new Set(prev);
				next.delete(module.id);
				return next;
			});
		}
	};

	if (userSubscriptions.length === 0) {
		return (
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<Target className="h-5 w-5" />
						Available Modules
					</CardTitle>
					<CardDescription>
						No modules installed. Browse the marketplace to add analysis tools.
					</CardDescription>
				</CardHeader>
				<CardContent>
					<Button asChild>
						<a href="/marketplace">Browse Marketplace</a>
					</Button>
				</CardContent>
			</Card>
		);
	}

	return (
		<div className="space-y-4">
			<div className="flex items-center justify-between">
				<h3 className="text-lg font-semibold flex items-center gap-2">
					<Target className="h-5 w-5" />
					Run Analysis Modules
				</h3>
				<span className="text-sm text-muted-foreground">
					{userSubscriptions.length} available
				</span>
			</div>

			<div
				className={`grid gap-4 ${compact ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2"}`}
			>
				{userSubscriptions.map((subscription) => {
					const { module } = subscription;
					const isRunning = runningModules.has(module.id);
					const result = results[module.id];
					const IconComponent = getModuleIcon(module.category);

					return (
						<Card key={module.id} className="relative">
							<CardHeader className="pb-3">
								<div className="flex items-start justify-between">
									<div className="flex items-center gap-2">
										<IconComponent className="h-5 w-5 text-primary" />
										<CardTitle className="text-base">
											{module.displayName}
										</CardTitle>
									</div>
									{subscription.licenseType === "premium" && (
										<Badge variant="secondary" className="text-xs">
											Premium
										</Badge>
									)}
								</div>
								<CardDescription className="text-sm">
									{module.description}
								</CardDescription>
							</CardHeader>

							<CardContent className="space-y-3">
								{/* Module capabilities */}
								<div className="flex flex-wrap gap-1">
									{module.capabilities.analysisTypes.slice(0, 2).map((type) => (
										<Badge key={type} variant="outline" className="text-xs">
											{type.replace("-", " ")}
										</Badge>
									))}
									{module.capabilities.analysisTypes.length > 2 && (
										<Badge variant="outline" className="text-xs">
											+{module.capabilities.analysisTypes.length - 2}
										</Badge>
									)}
								</div>

								{/* Execution controls */}
								<div className="flex gap-2">
									<Button
										size="sm"
										onClick={() => executeModule(module)}
										disabled={isRunning}
										className="flex-1"
									>
										{isRunning ? (
											<>
												<LoadingSpinner size="sm" />
												<span className="ml-2">Running...</span>
											</>
										) : (
											<>
												<Play className="h-4 w-4 mr-2" />
												Run Analysis
											</>
										)}
									</Button>

									<Button variant="outline" size="sm" asChild>
										<a href={`/my-modules/${module.id}/configure`}>
											<Settings className="h-4 w-4" />
										</a>
									</Button>
								</div>

								{/* Processing info */}
								<div className="text-xs text-muted-foreground flex items-center gap-4">
									<span className="flex items-center gap-1">
										<Clock className="h-3 w-3" />~
										{module.capabilities.estimatedProcessingTime}s
									</span>
									<span>Max {module.capabilities.maxFileSize}MB</span>
								</div>

								{/* Results */}
								{result && (
									<div className="mt-3 pt-3 border-t">
										<div className="flex items-center gap-2 mb-2">
											{result.status === "success" ? (
												<CheckCircle className="h-4 w-4 text-green-600" />
											) : (
												<AlertTriangle className="h-4 w-4 text-yellow-600" />
											)}
											<Badge className={getStatusColor(result.status)}>
												{result.status}
											</Badge>
											<span className="text-xs text-muted-foreground">
												{Math.round(result.results.confidence * 100)}%
												confidence
											</span>
										</div>

										<p className="text-sm mb-2">{result.results.summary}</p>

										{result.results.suggestions.length > 0 && (
											<Alert className="mt-2">
												<AlertTriangle className="h-4 w-4" />
												<AlertDescription className="text-sm">
													<strong>Suggestions:</strong>
													<ul className="list-disc list-inside mt-1">
														{result.results.suggestions
															.slice(0, 2)
															.map((suggestion, index) => (
																<li
																	key={`suggestion-${index}-${suggestion.slice(0, 20)}`}
																>
																	{suggestion}
																</li>
															))}
													</ul>
													{result.results.suggestions.length > 2 && (
														<p className="text-xs text-muted-foreground mt-1">
															+{result.results.suggestions.length - 2} more
															suggestions
														</p>
													)}
												</AlertDescription>
											</Alert>
										)}

										<div className="flex justify-between items-center mt-3 text-xs text-muted-foreground">
											<span>
												Processed: {result.processedPages}/{result.totalPages}{" "}
												pages
											</span>
											<Button variant="ghost" size="sm" className="h-auto p-1">
												View Full Report
											</Button>
										</div>
									</div>
								)}
							</CardContent>
						</Card>
					);
				})}
			</div>
		</div>
	);
};

export { ModuleRunner };
