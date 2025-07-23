/**
 * Marketplace Page - Browse and discover modules
 * Main marketplace interface with search, filters, and module grid
 */

import {
  Award,
  BookCheck,
  Crown,
  Database,
  Download,
  Filter,
  Lock,
  Palette,
  Search,
  Shield,
  Star,
  Store,
  Users,
  Verified,
  Zap,
} from "lucide-react";
import type React from "react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useMarketplace } from "@/hooks/useMarketplace";
import type { MarketplaceFilters } from "@/types/marketplace";

const categoryIcons = {
  citation: BookCheck,
  analysis: Shield,
  formatting: Palette,
  collaboration: Users,
  data: Database,
  security: Lock,
  automation: Zap,
};

const categoryColors = {
  citation: "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400",
  analysis:
    "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
  formatting:
    "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400",
  collaboration:
    "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400",
  data: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/20 dark:text-cyan-400",
  security: "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400",
  automation:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400",
};

const MarketplacePage: React.FC = () => {
  const {
    modules,
    marketplaceStats,
    loading,
    searchParams,
    setSearchParams,
    totalPages,
    isModuleSubscribed,
  } = useMarketplace();

  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState(searchParams.query || "");

  const handleSearch = (query: string) => {
    setSearchParams({
      ...searchParams,
      query: query.trim() || undefined,
      page: 1,
    });
  };

  const handleFilterChange = (filters: Partial<MarketplaceFilters>) => {
    setSearchParams({
      ...searchParams,
      filters: {
        ...searchParams.filters,
        ...filters,
      },
      page: 1,
    });
  };

  const handleSortChange = (sortBy: string) => {
    setSearchParams({
      ...searchParams,
      sortBy: sortBy as any,
      page: 1,
    });
  };

  const handlePageChange = (page: number) => {
    setSearchParams({
      ...searchParams,
      page,
    });
  };

  const formatPrice = (price?: number, currency = "USD") => {
    if (!price) return "Free";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
    }).format(price);
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

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Store className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Module Marketplace</h1>
        </div>
        <p className="text-muted-foreground text-lg">
          Discover powerful modules to enhance your document analysis workflow
        </p>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {marketplaceStats.totalModules}
              </div>
              <div className="text-sm text-muted-foreground">
                Available Modules
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {marketplaceStats.totalDownloads.toLocaleString()}
              </div>
              <div className="text-sm text-muted-foreground">
                Total Downloads
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">
                {marketplaceStats.featuredModules.length}
              </div>
              <div className="text-sm text-muted-foreground">
                Featured Modules
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6">
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search modules..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch(searchQuery)}
              className="pl-10"
            />
          </div>
          <Button onClick={() => handleSearch(searchQuery)}>Search</Button>
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
        </div>

        {/* Sort Controls */}
        <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
          <span className="text-sm text-muted-foreground">Sort by:</span>
          <Select value={searchParams.sortBy} onValueChange={handleSortChange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="popularity">Popularity</SelectItem>
              <SelectItem value="rating">Rating</SelectItem>
              <SelectItem value="newest">Newest</SelectItem>
              <SelectItem value="name">Name</SelectItem>
              <SelectItem value="price">Price</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-lg">Filters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Category Filter */}
                <div>
                  <h4 className="font-medium mb-3">Category</h4>
                  <div className="space-y-2">
                    {Object.keys(categoryIcons).map((category) => (
                      <div
                        key={category}
                        className="flex items-center space-x-2"
                      >
                        <Checkbox
                          id={`category-${category}`}
                          checked={
                            searchParams.filters?.category?.includes(
                              category,
                            ) || false
                          }
                          onCheckedChange={(checked: boolean) => {
                            const currentCategories =
                              searchParams.filters?.category || [];
                            const newCategories = checked
                              ? [...currentCategories, category]
                              : currentCategories.filter((c) => c !== category);
                            handleFilterChange({ category: newCategories });
                          }}
                        />
                        <label
                          htmlFor={`category-${category}`}
                          className="text-sm capitalize cursor-pointer"
                        >
                          {category}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* License Type Filter */}
                <div>
                  <h4 className="font-medium mb-3">License Type</h4>
                  <div className="space-y-2">
                    {["free", "freemium", "paid", "subscription"].map(
                      (type) => (
                        <div key={type} className="flex items-center space-x-2">
                          <Checkbox
                            id={`license-${type}`}
                            checked={
                              searchParams.filters?.licenseType?.includes(
                                type,
                              ) || false
                            }
                            onCheckedChange={(checked: boolean) => {
                              const currentTypes =
                                searchParams.filters?.licenseType || [];
                              const newTypes = checked
                                ? [...currentTypes, type]
                                : currentTypes.filter((t) => t !== type);
                              handleFilterChange({ licenseType: newTypes });
                            }}
                          />
                          <label
                            htmlFor={`license-${type}`}
                            className="text-sm capitalize cursor-pointer"
                          >
                            {type}
                          </label>
                        </div>
                      ),
                    )}
                  </div>
                </div>

                {/* Other Filters */}
                <div>
                  <h4 className="font-medium mb-3">Other Filters</h4>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="verified"
                        checked={searchParams.filters?.verified || false}
                        onCheckedChange={(checked: boolean) =>
                          handleFilterChange({ verified: checked || undefined })
                        }
                      />
                      <label
                        htmlFor="verified"
                        className="text-sm cursor-pointer"
                      >
                        Verified only
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="featured"
                        checked={searchParams.filters?.featured || false}
                        onCheckedChange={(checked: boolean) =>
                          handleFilterChange({ featured: checked || undefined })
                        }
                      />
                      <label
                        htmlFor="featured"
                        className="text-sm cursor-pointer"
                      >
                        Featured only
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Module Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
        {modules.map((module) => {
          const IconComponent = categoryIcons[module.category] || Award;
          const isSubscribed = isModuleSubscribed(module.id);

          return (
            <Card
              key={module.id}
              className="h-full flex flex-col hover:shadow-lg transition-shadow"
            >
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <IconComponent className="h-6 w-6 text-primary" />
                    {module.featured && (
                      <Crown className="h-4 w-4 text-yellow-500" />
                    )}
                    {module.verified && (
                      <Verified className="h-4 w-4 text-blue-500" />
                    )}
                  </div>
                  <Badge className={categoryColors[module.category]}>
                    {module.category}
                  </Badge>
                </div>
                <CardTitle className="text-lg">{module.displayName}</CardTitle>
                <CardDescription className="text-sm">
                  {module.description}
                </CardDescription>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col">
                <div className="mb-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                    <Star className="h-4 w-4 fill-current text-yellow-500" />
                    <span>{module.rating.average}</span>
                    <span>({module.rating.count})</span>
                    <Separator orientation="vertical" className="h-4" />
                    <Download className="h-4 w-4" />
                    <span>{module.downloads.toLocaleString()}</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    by {module.author.name}
                  </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {module.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {module.tags.length > 3 && (
                    <Badge variant="secondary" className="text-xs">
                      +{module.tags.length - 3}
                    </Badge>
                  )}
                </div>

                {/* Price and Action */}
                <div className="mt-auto">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-lg font-semibold">
                      {formatPrice(
                        module.license.price,
                        module.license.currency,
                      )}
                      {module.license.billingCycle && module.license.price && (
                        <span className="text-sm font-normal text-muted-foreground">
                          /{module.license.billingCycle}
                        </span>
                      )}
                    </div>
                    {module.license.trialPeriod && (
                      <Badge variant="outline" className="text-xs">
                        {module.license.trialPeriod}d trial
                      </Badge>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button asChild size="sm" className="flex-1">
                      <Link to={`/marketplace/modules/${module.id}`}>
                        View Details
                      </Link>
                    </Button>
                    {isSubscribed && (
                      <Badge variant="secondary" className="px-2 py-1">
                        Installed
                      </Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            onClick={() => handlePageChange((searchParams.page || 1) - 1)}
            disabled={(searchParams.page || 1) <= 1}
          >
            Previous
          </Button>

          <div className="flex gap-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={
                  (searchParams.page || 1) === page ? "default" : "outline"
                }
                size="sm"
                onClick={() => handlePageChange(page)}
              >
                {page}
              </Button>
            ))}
          </div>

          <Button
            variant="outline"
            onClick={() => handlePageChange((searchParams.page || 1) + 1)}
            disabled={(searchParams.page || 1) >= totalPages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
};

export default MarketplacePage;
