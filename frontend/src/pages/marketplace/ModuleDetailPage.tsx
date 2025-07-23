/**
 * Module Detail Page - Detailed view of a specific marketplace module
 * Shows full module information, configuration options, and installation
 */

import {
	ArrowLeft,
	BookOpen,
	Calendar,
	CheckCircle,
	Clock,
	Crown,
	Download,
	ExternalLink,
	Globe,
	HardDrive,
	Play,
	Settings,
	Shield,
	Star,
	Verified,
	XCircle,
} from "lucide-react";
import type React from "react";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ModuleConfigSidebar } from "@/components/modules/ModuleConfigSidebar";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useMarketplace } from "@/hooks/useMarketplace";

// Simple time formatter (alternative to date-fns)
const formatDistanceToNow = (date: Date) => {
	const now = new Date();
	const diffInMinutes = Math.floor(
		(now.getTime() - date.getTime()) / (1000 * 60),
	);

	if (diffInMinutes < 60) {
		return `${diffInMinutes} minutes ago`;
	} else if (diffInMinutes < 1440) {
		const hours = Math.floor(diffInMinutes / 60);
		return `${hours} ${hours === 1 ? "hour" : "hours"} ago`;
	} else {
		const days = Math.floor(diffInMinutes / 1440);
		return `${days} ${days === 1 ? "day" : "days"} ago`;
	}
};

const ModuleDetailPage: React.FC = () => {
	const { moduleId } = useParams<{ moduleId: string }>();
	const navigate = useNavigate();
	const {
		allModules,
		loading,
		isModuleSubscribed,
		subscribeToModule,
		unsubscribeFromModule,
		getUserSubscription,
	} = useMarketplace();

	const [installing, setInstalling] = useState(false);
	const [activeTab, setActiveTab] = useState("overview");
	const [configSidebarOpen, setConfigSidebarOpen] = useState(false);

	const openConfigSidebar = () => {
		if (module && subscription) {
			setConfigSidebarOpen(true);
		}
	};

	const handleSaveConfig = async (config: any) => {
		// TODO: Implement API call to save configuration
		console.log("Saving config for module:", module?.id, config);

		// Simulate API call
		await new Promise((resolve) => setTimeout(resolve, 1000));

		console.log("Configuration saved successfully");
	};

	const handleRevertConfig = () => {
		console.log("Reverting configuration changes");
	};

	const handleResetToDefault = () => {
		console.log("Resetting to default configuration");
	};

	const module = allModules.find((m) => m.id === moduleId);
	const isSubscribed = module ? isModuleSubscribed(module.id) : false;
	const subscription = module ? getUserSubscription(module.id) : null;

	if (loading) {
		return (
			<div className="container mx-auto px-4 py-8">
				<div className="flex items-center justify-center min-h-96">
					<LoadingSpinner size="lg" />
				</div>
			</div>
		);
	}

	if (!module) {
		return (
			<div className="container mx-auto px-4 py-8">
				<div className="text-center">
					<h1 className="text-2xl font-bold mb-4">Module Not Found</h1>
					<p className="text-muted-foreground mb-6">
						The requested module could not be found.
					</p>
					<Button onClick={() => navigate("/marketplace")}>
						<ArrowLeft className="h-4 w-4 mr-2" />
						Back to Marketplace
					</Button>
				</div>
			</div>
		);
	}

	const handleInstall = async (licenseType: "free" | "premium") => {
		setInstalling(true);
		try {
			await subscribeToModule(module.id, licenseType);
		} finally {
			setInstalling(false);
		}
	};

	const handleUninstall = async () => {
		setInstalling(true);
		try {
			await unsubscribeFromModule(module.id);
		} finally {
			setInstalling(false);
		}
	};

	const formatFileSize = (bytes: number) => {
		const sizes = ["Bytes", "KB", "MB", "GB"];
		if (bytes === 0) return "0 Bytes";
		const i = Math.floor(Math.log(bytes) / Math.log(1024));
		return `${Math.round((bytes / 1024 ** i) * 100) / 100} ${sizes[i]}`;
	};

	const formatPrice = (price?: number, currency = "USD") => {
		if (!price) return "Free";
		return new Intl.NumberFormat("en-US", {
			style: "currency",
			currency,
		}).format(price);
	};

	return (
		<div className="container mx-auto px-4 py-8">
			{/* Back Button */}
			<Button
				variant="outline"
				onClick={() => navigate("/marketplace")}
				className="mb-6"
			>
				<ArrowLeft className="h-4 w-4 mr-2" />
				Back to Marketplace
			</Button>

			{/* Module Header */}
			<div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
				{/* Main Info */}
				<div className="lg:col-span-2">
					<div className="flex items-start gap-4 mb-6">
						<div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center">
							<Shield className="h-8 w-8 text-primary" />
						</div>
						<div className="flex-1">
							<div className="flex items-center gap-2 mb-2">
								<h1 className="text-3xl font-bold">{module.displayName}</h1>
								{module.featured && (
									<Crown className="h-5 w-5 text-yellow-500" />
								)}
								{module.verified && (
									<Verified className="h-5 w-5 text-blue-500" />
								)}
							</div>
							<p className="text-lg text-muted-foreground mb-4">
								{module.description}
							</p>

							{/* Author Info */}
							<div className="flex items-center gap-3">
								<div className="h-8 w-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
									{module.author.name
										.split(" ")
										.map((n) => n[0])
										.join("")}
								</div>
								<div>
									<div className="font-medium">{module.author.name}</div>
									{module.author.organization && (
										<div className="text-sm text-muted-foreground">
											{module.author.organization}
										</div>
									)}
								</div>
								{module.author.verified && (
									<Verified className="h-4 w-4 text-blue-500" />
								)}
							</div>
						</div>
					</div>

					{/* Stats */}
					<div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
						<div className="text-center">
							<div className="flex items-center justify-center gap-1 mb-1">
								<Star className="h-4 w-4 fill-current text-yellow-500" />
								<span className="font-semibold">{module.rating.average}</span>
							</div>
							<div className="text-sm text-muted-foreground">
								{module.rating.count} reviews
							</div>
						</div>
						<div className="text-center">
							<div className="flex items-center justify-center gap-1 mb-1">
								<Download className="h-4 w-4" />
								<span className="font-semibold">
									{module.downloads.toLocaleString()}
								</span>
							</div>
							<div className="text-sm text-muted-foreground">downloads</div>
						</div>
						<div className="text-center">
							<div className="flex items-center justify-center gap-1 mb-1">
								<Calendar className="h-4 w-4" />
								<span className="font-semibold">v{module.currentVersion}</span>
							</div>
							<div className="text-sm text-muted-foreground">
								{formatDistanceToNow(new Date(module.updatedAt))}
							</div>
						</div>
						<div className="text-center">
							<div className="flex items-center justify-center gap-1 mb-1">
								<HardDrive className="h-4 w-4" />
								<span className="font-semibold">
									{formatFileSize(module.versions[0]?.size || 0)}
								</span>
							</div>
							<div className="text-sm text-muted-foreground">download size</div>
						</div>
					</div>

					{/* Tags */}
					<div className="flex flex-wrap gap-2 mb-6">
						{module.tags.map((tag) => (
							<Badge key={tag} variant="secondary">
								{tag}
							</Badge>
						))}
					</div>
				</div>

				{/* Installation Panel */}
				<div className="lg:col-span-1">
					<Card>
						<CardHeader>
							<CardTitle>Installation</CardTitle>
							<CardDescription>
								{isSubscribed
									? "Module is installed"
									: "Add this module to your toolkit"}
							</CardDescription>
						</CardHeader>
						<CardContent>
							{isSubscribed ? (
								<div className="space-y-4">
									<div className="flex items-center gap-2 text-green-600">
										<CheckCircle className="h-5 w-5" />
										<span className="font-medium">Installed</span>
									</div>

									{subscription && (
										<div className="space-y-2 text-sm">
											<div>
												License:{" "}
												<span className="font-medium capitalize">
													{subscription.licenseType}
												</span>
											</div>
											{subscription.expiresAt && (
												<div>
													Expires:{" "}
													<span className="font-medium">
														{new Date(
															subscription.expiresAt,
														).toLocaleDateString()}
													</span>
												</div>
											)}
											<div>
												Usage:{" "}
												<span className="font-medium">
													{subscription.usageStats.totalRuns} runs
												</span>
											</div>
										</div>
									)}

									<div className="space-y-2">
										<Button className="w-full" onClick={openConfigSidebar}>
											<Settings className="h-4 w-4 mr-2" />
											Configure
										</Button>

										<Button
											variant="outline"
											size="sm"
											className="w-full"
											onClick={handleUninstall}
											disabled={installing}
										>
											{installing ? (
												<LoadingSpinner size="sm" />
											) : (
												<XCircle className="h-4 w-4 mr-2" />
											)}
											Uninstall
										</Button>
									</div>
								</div>
							) : (
								<div className="space-y-4">
									{/* Pricing */}
									<div>
										<div className="text-2xl font-bold">
											{formatPrice(
												module.license.price,
												module.license.currency,
											)}
											{module.license.billingCycle && module.license.price && (
												<span className="text-lg font-normal text-muted-foreground">
													/{module.license.billingCycle}
												</span>
											)}
										</div>
										{module.license.trialPeriod && (
											<div className="text-sm text-muted-foreground">
												{module.license.trialPeriod} day free trial
											</div>
										)}
									</div>

									{/* Install Buttons */}
									<div className="space-y-2">
										{module.license.type === "free" && (
											<Button
												className="w-full"
												onClick={() => handleInstall("free")}
												disabled={installing}
											>
												{installing ? (
													<LoadingSpinner size="sm" />
												) : (
													<Download className="h-4 w-4 mr-2" />
												)}
												Install Free
											</Button>
										)}

										{(module.license.type === "freemium" ||
											module.license.type === "paid") && (
											<>
												{module.license.features.free.length > 0 && (
													<Button
														variant="outline"
														className="w-full"
														onClick={() => handleInstall("free")}
														disabled={installing}
													>
														{installing ? (
															<LoadingSpinner size="sm" />
														) : (
															<Download className="h-4 w-4 mr-2" />
														)}
														Try Free Version
													</Button>
												)}
												<Button
													className="w-full"
													onClick={() => handleInstall("premium")}
													disabled={installing}
												>
													{installing ? (
														<LoadingSpinner size="sm" />
													) : (
														<Download className="h-4 w-4 mr-2" />
													)}
													{module.license.trialPeriod
														? "Start Free Trial"
														: "Get Premium"}
												</Button>
											</>
										)}

										{module.license.type === "subscription" && (
											<Button
												className="w-full"
												onClick={() => handleInstall("premium")}
												disabled={installing}
											>
												{installing ? (
													<LoadingSpinner size="sm" />
												) : (
													<Download className="h-4 w-4 mr-2" />
												)}
												{module.license.trialPeriod
													? "Start Free Trial"
													: "Subscribe"}
											</Button>
										)}
									</div>

									{/* Quick Links */}
									<div className="space-y-2 pt-4 border-t">
										{module.demoUrl && (
											<Button
												variant="ghost"
												size="sm"
												className="w-full"
												asChild
											>
												<a
													href={module.demoUrl}
													target="_blank"
													rel="noopener noreferrer"
												>
													<Play className="h-4 w-4 mr-2" />
													Try Demo
													<ExternalLink className="h-3 w-3 ml-1" />
												</a>
											</Button>
										)}

										<Button
											variant="ghost"
											size="sm"
											className="w-full"
											asChild
										>
											<a
												href={module.documentation}
												target="_blank"
												rel="noopener noreferrer"
											>
												<BookOpen className="h-4 w-4 mr-2" />
												Documentation
												<ExternalLink className="h-3 w-3 ml-1" />
											</a>
										</Button>

										{module.sourceCodeUrl && (
											<Button
												variant="ghost"
												size="sm"
												className="w-full"
												asChild
											>
												<a
													href={module.sourceCodeUrl}
													target="_blank"
													rel="noopener noreferrer"
												>
													<Globe className="h-4 w-4 mr-2" />
													Source Code
													<ExternalLink className="h-3 w-3 ml-1" />
												</a>
											</Button>
										)}
									</div>
								</div>
							)}
						</CardContent>
					</Card>
				</div>
			</div>

			{/* Detailed Information Tabs */}
			<Tabs value={activeTab} onValueChange={setActiveTab}>
				<TabsList className="grid w-full grid-cols-4">
					<TabsTrigger value="overview">Overview</TabsTrigger>
					<TabsTrigger value="features">Features</TabsTrigger>
					<TabsTrigger value="reviews">Reviews</TabsTrigger>
					<TabsTrigger value="changelog">Changelog</TabsTrigger>
				</TabsList>

				<TabsContent value="overview" className="mt-6">
					<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
						{/* Description */}
						<Card>
							<CardHeader>
								<CardTitle>About this Module</CardTitle>
							</CardHeader>
							<CardContent>
								<p className="text-muted-foreground leading-relaxed">
									{module.longDescription}
								</p>
							</CardContent>
						</Card>

						{/* Capabilities */}
						<Card>
							<CardHeader>
								<CardTitle>Capabilities</CardTitle>
							</CardHeader>
							<CardContent className="space-y-4">
								<div>
									<h4 className="font-medium mb-2">Analysis Types</h4>
									<div className="flex flex-wrap gap-1">
										{module.capabilities.analysisTypes.map((type) => (
											<Badge key={type} variant="outline" className="text-xs">
												{type.replace("-", " ")}
											</Badge>
										))}
									</div>
								</div>

								<div>
									<h4 className="font-medium mb-2">Supported Formats</h4>
									<div className="flex flex-wrap gap-1">
										{module.capabilities.supportedFormats.map((format) => (
											<Badge
												key={format}
												variant="secondary"
												className="text-xs"
											>
												.{format}
											</Badge>
										))}
									</div>
								</div>

								<div>
									<h4 className="font-medium mb-2">Languages</h4>
									<div className="flex flex-wrap gap-1">
										{module.capabilities.supportedLanguages.map((lang) => (
											<Badge key={lang} variant="outline" className="text-xs">
												{lang.toUpperCase()}
											</Badge>
										))}
									</div>
								</div>

								<div className="grid grid-cols-2 gap-4 pt-2">
									<div className="text-sm">
										<div className="font-medium">Processing Time</div>
										<div className="text-muted-foreground flex items-center gap-1">
											<Clock className="h-3 w-3" />~
											{module.capabilities.estimatedProcessingTime}s
										</div>
									</div>
									<div className="text-sm">
										<div className="font-medium">Max File Size</div>
										<div className="text-muted-foreground flex items-center gap-1">
											<HardDrive className="h-3 w-3" />
											{module.capabilities.maxFileSize}MB
										</div>
									</div>
								</div>
							</CardContent>
						</Card>
					</div>
				</TabsContent>

				<TabsContent value="features" className="mt-6">
					<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
						{/* Free Features */}
						<Card>
							<CardHeader>
								<CardTitle>Free Features</CardTitle>
								<CardDescription>
									Available with the free version
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="space-y-2">
									{module.license.features.free.map((feature, index) => (
										<li
											key={`free-${feature.slice(0, 20)}-${index}`}
											className="flex items-start gap-2"
										>
											<CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
											<span className="text-sm">{feature}</span>
										</li>
									))}
								</ul>
							</CardContent>
						</Card>

						{/* Premium Features */}
						{module.license.features.premium && (
							<Card>
								<CardHeader>
									<CardTitle>Premium Features</CardTitle>
									<CardDescription>
										Available with premium subscription
									</CardDescription>
								</CardHeader>
								<CardContent>
									<ul className="space-y-2">
										{module.license.features.premium.map((feature, index) => (
											<li
												key={`premium-${feature.slice(0, 20)}-${index}`}
												className="flex items-start gap-2"
											>
												<Crown className="h-4 w-4 text-yellow-500 mt-0.5" />
												<span className="text-sm">{feature}</span>
											</li>
										))}
									</ul>
								</CardContent>
							</Card>
						)}
					</div>
				</TabsContent>

				<TabsContent value="reviews" className="mt-6">
					<Card>
						<CardHeader>
							<CardTitle>User Reviews</CardTitle>
							<CardDescription>
								{module.rating.count} reviews • Average {module.rating.average}
								/5
							</CardDescription>
						</CardHeader>
						<CardContent>
							<div className="text-center text-muted-foreground py-8">
								Reviews feature coming soon
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				<TabsContent value="changelog" className="mt-6">
					<Card>
						<CardHeader>
							<CardTitle>Version History</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="space-y-4">
								{module.versions.map((version) => (
									<div
										key={version.version}
										className="border-l-2 border-muted pl-4"
									>
										<div className="flex items-center gap-2 mb-2">
											<span className="font-semibold">v{version.version}</span>
											<span className="text-sm text-muted-foreground">
												{new Date(version.releaseDate).toLocaleDateString()}
											</span>
											<Badge variant="outline" className="text-xs">
												{formatFileSize(version.size)}
											</Badge>
										</div>
										<p className="text-sm text-muted-foreground">
											{version.changelog}
										</p>
									</div>
								))}
							</div>
						</CardContent>
					</Card>
				</TabsContent>
			</Tabs>

			{/* Module Configuration Sidebar */}
			<ModuleConfigSidebar
				isOpen={configSidebarOpen}
				onClose={() => setConfigSidebarOpen(false)}
				module={
					isSubscribed && subscription
						? {
								id: module.id,
								name: module.displayName || module.name,
								version: module.currentVersion,
								description: module.description,
								configSchema: module.configuration || {},
								userConfig: subscription.configuration || {},
								defaultConfig: Object.keys(module.configuration || {}).reduce(
									(acc, key) => {
										acc[key] = module.configuration?.[key].default;
										return acc;
									},
									{} as any,
								),
							}
						: null
				}
				onSave={handleSaveConfig}
				onRevert={handleRevertConfig}
				onResetToDefault={handleResetToDefault}
			/>
		</div>
	);
};

export default ModuleDetailPage;
