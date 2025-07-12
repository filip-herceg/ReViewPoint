/**
 * My Modules Page - Manage user's subscribed modules
 * Shows installed modules, configuration, and usage statistics
 */

import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Progress } from "@/components/ui/progress";
import { ModuleConfigSidebar } from "@/components/modules/ModuleConfigSidebar";
import {
  Settings,
  BarChart3,
  Calendar,
  Clock,
  Play,
  Trash2,
  ExternalLink,
  Package,
  Crown,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";
import { useMarketplace } from "@/hooks/useMarketplace";

const MyModulesPage: React.FC = () => {
  const { userSubscriptions, loading, unsubscribeFromModule } =
    useMarketplace();

  const [configSidebarOpen, setConfigSidebarOpen] = useState(false);
  const [selectedModule, setSelectedModule] = useState<any>(null);

  const openConfigSidebar = (module: any, subscription: any) => {
    // Combine module and subscription data for configuration
    setSelectedModule({
      id: module.id,
      name: module.displayName || module.name,
      version: module.currentVersion,
      description: module.description,
      configSchema: module.configuration || {},
      userConfig: subscription.configuration || {},
      defaultConfig: Object.keys(module.configuration || {}).reduce(
        (acc, key) => {
          acc[key] = module.configuration![key].default;
          return acc;
        },
        {} as any,
      ),
    });
    setConfigSidebarOpen(true);
  };

  const handleSaveConfig = async (config: any) => {
    // TODO: Implement API call to save configuration
    console.log("Saving config for module:", selectedModule?.id, config);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Update local state or refetch data
    console.log("Configuration saved successfully");
  };

  const handleRevertConfig = () => {
    console.log("Reverting configuration changes");
  };

  const handleResetToDefault = () => {
    console.log("Resetting to default configuration");
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-96">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "trial":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
      case "expired":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
      case "cancelled":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="h-4 w-4" />;
      case "trial":
        return <Clock className="h-4 w-4" />;
      case "expired":
      case "cancelled":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Package className="h-8 w-8 text-primary" />
              <h1 className="text-3xl font-bold">My Modules</h1>
            </div>
            <p className="text-muted-foreground">
              Manage your installed modules and subscriptions
            </p>
          </div>
          <Button asChild>
            <Link to="/marketplace">
              <Package className="h-4 w-4 mr-2" />
              Browse Marketplace
            </Link>
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {userSubscriptions.length}
              </div>
              <div className="text-sm text-muted-foreground">Total Modules</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {userSubscriptions.filter((s) => s.status === "active").length}
              </div>
              <div className="text-sm text-muted-foreground">Active</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {userSubscriptions.reduce(
                  (sum, s) => sum + s.usageStats.totalRuns,
                  0,
                )}
              </div>
              <div className="text-sm text-muted-foreground">Total Runs</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {
                  userSubscriptions.filter((s) => s.licenseType === "premium")
                    .length
                }
              </div>
              <div className="text-sm text-muted-foreground">Premium</div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modules List */}
      {userSubscriptions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Package className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No modules installed</h3>
            <p className="text-muted-foreground text-center mb-6">
              Browse the marketplace to discover and install powerful modules
              for your workflow
            </p>
            <Button asChild>
              <Link to="/marketplace">Browse Marketplace</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {userSubscriptions.map((subscription) => {
            const { module } = subscription;

            return (
              <Card key={subscription.moduleId} className="overflow-hidden">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <CardTitle className="text-xl">
                          {module.displayName}
                        </CardTitle>
                        <Badge className={getStatusColor(subscription.status)}>
                          {getStatusIcon(subscription.status)}
                          <span className="ml-1 capitalize">
                            {subscription.status}
                          </span>
                        </Badge>
                        {subscription.licenseType === "premium" && (
                          <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
                            <Crown className="h-3 w-3 mr-1" />
                            Premium
                          </Badge>
                        )}
                      </div>
                      <CardDescription>{module.description}</CardDescription>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openConfigSidebar(module, subscription)}
                      >
                        <Settings className="h-4 w-4 mr-2" />
                        Configure
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/marketplace/modules/${module.id}`}>
                          <ExternalLink className="h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Usage Statistics */}
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <BarChart3 className="h-4 w-4" />
                        Usage Statistics
                      </h4>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Total Runs</span>
                            <span className="font-medium">
                              {subscription.usageStats.totalRuns}
                            </span>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Avg. Processing Time</span>
                            <span className="font-medium">
                              {subscription.usageStats.averageProcessingTime}s
                            </span>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Last Used</span>
                            <span className="font-medium">
                              {formatDate(subscription.usageStats.lastUsed)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Subscription Details */}
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        Subscription Details
                      </h4>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Subscribed</span>
                            <span className="font-medium">
                              {formatDate(subscription.subscribedAt)}
                            </span>
                          </div>
                        </div>
                        {subscription.expiresAt && (
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>Expires</span>
                              <span className="font-medium">
                                {formatDate(subscription.expiresAt)}
                              </span>
                            </div>
                            {/* Show progress if there's an expiration */}
                            {subscription.status === "active" && (
                              <div className="mt-2">
                                <Progress
                                  value={(() => {
                                    const now = new Date().getTime();
                                    const start = new Date(
                                      subscription.subscribedAt,
                                    ).getTime();
                                    const end = new Date(
                                      subscription.expiresAt,
                                    ).getTime();
                                    const progress =
                                      ((now - start) / (end - start)) * 100;
                                    return Math.min(Math.max(progress, 0), 100);
                                  })()}
                                  className="h-2"
                                />
                                <div className="text-xs text-muted-foreground mt-1">
                                  Time remaining
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Version</span>
                            <span className="font-medium">
                              v{module.currentVersion}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Play className="h-4 w-4" />
                        Quick Actions
                      </h4>
                      <div className="space-y-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full"
                          asChild
                        >
                          <Link to={`/uploads?module=${module.id}`}>
                            <Play className="h-4 w-4 mr-2" />
                            Run on Document
                          </Link>
                        </Button>

                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full"
                          asChild
                        >
                          <Link to={`/my-modules/${module.id}/history`}>
                            <BarChart3 className="h-4 w-4 mr-2" />
                            View History
                          </Link>
                        </Button>

                        {subscription.status === "active" && (
                          <Button
                            variant="destructive"
                            size="sm"
                            className="w-full"
                            onClick={() => unsubscribeFromModule(module.id)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Uninstall
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Module Configuration Sidebar */}
      <ModuleConfigSidebar
        isOpen={configSidebarOpen}
        onClose={() => setConfigSidebarOpen(false)}
        module={selectedModule}
        onSave={handleSaveConfig}
        onRevert={handleRevertConfig}
        onResetToDefault={handleResetToDefault}
      />
    </div>
  );
};

export default MyModulesPage;
