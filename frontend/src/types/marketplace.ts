/**
 * Types for Marketplace and Module System
 * Defines interfaces for modules, marketplace functionality, and user subscriptions
 */

export interface ModuleAuthor {
	id: string;
	name: string;
	email: string;
	organization?: string;
	avatar?: string;
	verified: boolean;
	reputation: number;
}

export interface ModuleVersion {
	version: string;
	releaseDate: string;
	changelog: string;
	downloadUrl: string;
	size: number; // in bytes
	requirements: string[];
	isCompatible: boolean;
}

export interface ModuleRating {
	userId: string;
	userName: string;
	rating: number; // 1-5
	review?: string;
	date: string;
	verified: boolean; // if user actually used the module
}

export interface ModuleLicense {
	type: "free" | "freemium" | "paid" | "subscription";
	price?: number;
	currency?: string;
	billingCycle?: "monthly" | "yearly" | "one-time";
	trialPeriod?: number; // days
	features: {
		free: string[];
		premium?: string[];
	};
}

export interface ModuleCapabilities {
	// What type of analysis the module can perform
	analysisTypes: (
		| "citation-validation"
		| "plagiarism-check"
		| "quality-assessment"
		| "bias-detection"
		| "methodology-review"
		| "data-extraction"
		| "formatting-check"
		| "language-analysis"
		| "statistical-validation"
	)[];

	// File formats it can process
	supportedFormats: ("pdf" | "docx" | "tex" | "md" | "txt" | "html")[];

	// Languages it supports
	supportedLanguages: string[];

	// Processing requirements
	requiresInternet: boolean;
	estimatedProcessingTime: number; // in seconds
	maxFileSize: number; // in MB
}

export interface ModuleConfiguration {
	[key: string]: {
		type: "string" | "number" | "boolean" | "select" | "multiselect";
		label: string;
		description?: string;
		required: boolean;
		default?: any;
		options?: Array<{ value: any; label: string }>;
		min?: number;
		max?: number;
	};
}

export interface Module {
	id: string;
	name: string;
	displayName: string;
	description: string;
	longDescription: string;
	icon: string;
	category:
		| "citation"
		| "analysis"
		| "formatting"
		| "collaboration"
		| "data"
		| "security"
		| "automation";
	tags: string[];

	// Author and versioning
	author: ModuleAuthor;
	currentVersion: string;
	versions: ModuleVersion[];

	// Marketplace metadata
	license: ModuleLicense;
	downloads: number;
	rating: {
		average: number;
		count: number;
	};
	reviews: ModuleRating[];

	// Technical specifications
	capabilities: ModuleCapabilities;
	configuration: ModuleConfiguration;

	// Media and documentation
	screenshots: string[];
	documentation: string;
	demoUrl?: string;
	sourceCodeUrl?: string;

	// Marketplace status
	status: "active" | "deprecated" | "beta" | "coming-soon";
	featured: boolean;
	verified: boolean;

	// Dates
	createdAt: string;
	updatedAt: string;
	publishedAt: string;
}

export interface UserModuleSubscription {
	moduleId: string;
	module: Module;
	subscribedAt: string;
	licenseType: "free" | "premium";
	expiresAt?: string;
	status: "active" | "expired" | "cancelled" | "trial";
	configuration: Record<string, any>;
	usageStats: {
		totalRuns: number;
		lastUsed: string;
		averageProcessingTime: number;
	};
}

export interface ModuleExecutionResult {
	moduleId: string;
	executionId: string;
	documentId: string;
	startTime: string;
	endTime: string;
	status: "success" | "error" | "warning";
	results: {
		summary: string;
		details: any;
		confidence: number; // 0-1
		suggestions: string[];
		warnings: string[];
		errors: string[];
	};
	processedPages?: number;
	totalPages?: number;
}

// Marketplace filter and search types
export interface MarketplaceFilters {
	category?: string[];
	licenseType?: string[];
	rating?: number;
	verified?: boolean;
	featured?: boolean;
	supportedFormats?: string[];
	analysisTypes?: string[];
	priceRange?: {
		min: number;
		max: number;
	};
}

export interface MarketplaceSearchParams {
	query?: string;
	filters?: MarketplaceFilters;
	sortBy?: "popularity" | "rating" | "newest" | "name" | "price";
	sortOrder?: "asc" | "desc";
	page?: number;
	limit?: number;
}

export interface MarketplaceStats {
	totalModules: number;
	totalDownloads: number;
	topCategories: Array<{ category: string; count: number }>;
	featuredModules: Module[];
	recentlyUpdated: Module[];
}

// Module execution context
export interface ModuleExecutionContext {
	documentId: string;
	userId: string;
	configuration: Record<string, any>;
	metadata: {
		fileName: string;
		fileSize: number;
		uploadDate: string;
		documentType: string;
	};
}
