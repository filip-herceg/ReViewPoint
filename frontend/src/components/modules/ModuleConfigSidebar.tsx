import {
	AlertTriangle,
	Info,
	RotateCcw,
	Save,
	Settings,
	X,
} from "lucide-react";
import type React from "react";
import { useEffect, useState } from "react";
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
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface ModuleConfig {
	[key: string]: any;
}

interface ModuleConfigSidebarProps {
	isOpen: boolean;
	onClose: () => void;
	module: {
		id: string;
		name: string;
		version: string;
		description: string;
		configSchema?: any;
		defaultConfig?: ModuleConfig;
		userConfig?: ModuleConfig;
	} | null;
	onSave: (config: ModuleConfig) => Promise<void>;
	onRevert: () => void;
	onResetToDefault: () => void;
}

export const ModuleConfigSidebar: React.FC<ModuleConfigSidebarProps> = ({
	isOpen,
	onClose,
	module,
	onSave,
	onRevert,
	onResetToDefault,
}) => {
	const [config, setConfig] = useState<ModuleConfig>({});
	const [hasChanges, setHasChanges] = useState(false);
	const [isSaving, setIsSaving] = useState(false);

	// Initialize config when module changes
	useEffect(() => {
		if (module) {
			const initialConfig = module.userConfig || module.defaultConfig || {};
			setConfig(initialConfig);
			setHasChanges(false);
		}
	}, [module]);

	// Check for changes
	useEffect(() => {
		if (module) {
			const originalConfig = module.userConfig || module.defaultConfig || {};
			setHasChanges(JSON.stringify(config) !== JSON.stringify(originalConfig));
		}
	}, [config, module]);

	const handleConfigChange = (key: string, value: any) => {
		setConfig((prev) => ({
			...prev,
			[key]: value,
		}));
	};

	const handleSave = async () => {
		if (!module || !hasChanges) return;

		setIsSaving(true);
		try {
			await onSave(config);
			setHasChanges(false);
		} catch (error) {
			console.error("Failed to save config:", error);
		} finally {
			setIsSaving(false);
		}
	};

	const handleRevert = () => {
		if (module) {
			const originalConfig = module.userConfig || module.defaultConfig || {};
			setConfig(originalConfig);
			setHasChanges(false);
			onRevert();
		}
	};

	const handleResetToDefault = () => {
		if (module?.defaultConfig) {
			setConfig(module.defaultConfig);
			onResetToDefault();
		}
	};

	const renderConfigField = (key: string, value: any, schema?: any) => {
		const fieldSchema = schema?.properties?.[key];
		const fieldType = fieldSchema?.type || typeof value;
		const fieldDescription = fieldSchema?.description;
		const fieldTitle = fieldSchema?.title || key;

		switch (fieldType) {
			case "boolean":
				return (
					<div key={key} className="space-y-2">
						<div className="flex items-center justify-between">
							<Label htmlFor={key} className="text-sm font-medium">
								{fieldTitle}
							</Label>
							<input
								id={key}
								type="checkbox"
								checked={value || false}
								onChange={(e) => handleConfigChange(key, e.target.checked)}
								className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-2 focus:ring-ring focus:ring-offset-2"
							/>
						</div>
						{fieldDescription && (
							<p className="text-xs text-muted-foreground">
								{fieldDescription}
							</p>
						)}
					</div>
				);

			case "number":
				return (
					<div key={key} className="space-y-2">
						<Label htmlFor={key} className="text-sm font-medium">
							{fieldTitle}
						</Label>
						<Input
							id={key}
							type="number"
							value={value || ""}
							onChange={(e) =>
								handleConfigChange(key, parseFloat(e.target.value) || 0)
							}
							min={fieldSchema?.minimum}
							max={fieldSchema?.maximum}
						/>
						{fieldDescription && (
							<p className="text-xs text-muted-foreground">
								{fieldDescription}
							</p>
						)}
					</div>
				);

			case "string":
				if (fieldSchema?.enum) {
					return (
						<div key={key} className="space-y-2">
							<Label htmlFor={key} className="text-sm font-medium">
								{fieldTitle}
							</Label>
							<select
								id={key}
								value={value || ""}
								onChange={(e) => handleConfigChange(key, e.target.value)}
								className="w-full px-3 py-2 text-sm border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
							>
								{fieldSchema.enum.map((option: string) => (
									<option key={option} value={option}>
										{option}
									</option>
								))}
							</select>
							{fieldDescription && (
								<p className="text-xs text-muted-foreground">
									{fieldDescription}
								</p>
							)}
						</div>
					);
				} else if (fieldSchema?.format === "textarea") {
					return (
						<div key={key} className="space-y-2">
							<Label htmlFor={key} className="text-sm font-medium">
								{fieldTitle}
							</Label>
							<Textarea
								id={key}
								value={value || ""}
								onChange={(e) => handleConfigChange(key, e.target.value)}
								rows={3}
							/>
							{fieldDescription && (
								<p className="text-xs text-muted-foreground">
									{fieldDescription}
								</p>
							)}
						</div>
					);
				} else {
					return (
						<div key={key} className="space-y-2">
							<Label htmlFor={key} className="text-sm font-medium">
								{fieldTitle}
							</Label>
							<Input
								id={key}
								type="text"
								value={value || ""}
								onChange={(e) => handleConfigChange(key, e.target.value)}
							/>
							{fieldDescription && (
								<p className="text-xs text-muted-foreground">
									{fieldDescription}
								</p>
							)}
						</div>
					);
				}

			default:
				return (
					<div key={key} className="space-y-2">
						<Label htmlFor={key} className="text-sm font-medium">
							{fieldTitle}
						</Label>
						<Input
							id={key}
							type="text"
							value={JSON.stringify(value) || ""}
							onChange={(e) => {
								try {
									const parsedValue = JSON.parse(e.target.value);
									handleConfigChange(key, parsedValue);
								} catch {
									handleConfigChange(key, e.target.value);
								}
							}}
						/>
						{fieldDescription && (
							<p className="text-xs text-muted-foreground">
								{fieldDescription}
							</p>
						)}
					</div>
				);
		}
	};

	if (!isOpen) return null;

	return (
		<>
			{/* Backdrop */}
			<div className="fixed inset-0 bg-black/20 z-40" onClick={onClose} />

			{/* Sidebar */}
			<div
				className={cn(
					"fixed top-0 right-0 h-full w-96 bg-background border-l border-border shadow-xl z-50 transform transition-transform duration-300",
					isOpen ? "translate-x-0" : "translate-x-full",
				)}
			>
				<div className="flex flex-col h-full">
					{/* Header */}
					<div className="flex items-center justify-between p-4 border-b border-border">
						<div className="flex items-center space-x-2">
							<Settings className="h-5 w-5 text-primary" />
							<h2 className="text-lg font-semibold">Configure Module</h2>
						</div>
						<Button variant="ghost" size="sm" onClick={onClose}>
							<X className="h-4 w-4" />
						</Button>
					</div>

					{/* Content */}
					<div className="flex-1 overflow-y-auto">
						<div className="p-4 space-y-6">
							{module && (
								<>
									{/* Module Info */}
									<Card>
										<CardHeader className="pb-3">
											<CardTitle className="text-base">{module.name}</CardTitle>
											<CardDescription className="text-sm">
												{module.description}
											</CardDescription>
										</CardHeader>
										<CardContent className="pt-0">
											<div className="flex items-center space-x-2">
												<Badge variant="secondary">v{module.version}</Badge>
												{hasChanges && (
													<Badge
														variant="outline"
														className="text-yellow-600 border-yellow-600"
													>
														<AlertTriangle className="h-3 w-3 mr-1" />
														Unsaved Changes
													</Badge>
												)}
											</div>
										</CardContent>
									</Card>

									<Separator />

									{/* Configuration Fields */}
									<div className="space-y-4">
										<div className="flex items-center space-x-2">
											<Settings className="h-4 w-4" />
											<h3 className="font-medium">Configuration</h3>
										</div>

										{Object.keys(config).length > 0 ? (
											<div className="space-y-4">
												{Object.entries(config).map(([key, value]) =>
													renderConfigField(key, value, module.configSchema),
												)}
											</div>
										) : (
											<div className="flex items-center space-x-2 p-4 bg-muted rounded-lg">
												<Info className="h-4 w-4 text-muted-foreground" />
												<p className="text-sm text-muted-foreground">
													This module has no configuration options.
												</p>
											</div>
										)}
									</div>

									{/* Help Text */}
									{module.configSchema?.description && (
										<Card className="bg-blue-50/50 border-blue-200">
											<CardContent className="p-4">
												<div className="flex items-start space-x-2">
													<Info className="h-4 w-4 text-blue-600 mt-0.5" />
													<p className="text-sm text-blue-700">
														{module.configSchema.description}
													</p>
												</div>
											</CardContent>
										</Card>
									)}
								</>
							)}
						</div>
					</div>

					{/* Footer Actions */}
					<div className="p-4 border-t border-border bg-muted/20">
						<div className="flex flex-col space-y-2">
							<div className="flex space-x-2">
								<Button
									onClick={handleSave}
									disabled={!hasChanges || isSaving}
									className="flex-1"
								>
									<Save className="h-4 w-4 mr-2" />
									{isSaving ? "Saving..." : "Save Changes"}
								</Button>
								<Button
									variant="outline"
									onClick={handleRevert}
									disabled={!hasChanges}
								>
									<RotateCcw className="h-4 w-4 mr-2" />
									Revert
								</Button>
							</div>

							{module?.defaultConfig && (
								<Button
									variant="ghost"
									size="sm"
									onClick={handleResetToDefault}
									className="w-full"
								>
									Reset to Default
								</Button>
							)}
						</div>
					</div>
				</div>
			</div>
		</>
	);
};
