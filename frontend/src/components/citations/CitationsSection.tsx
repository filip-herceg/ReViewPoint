import {
  BookMarked,
  Download,
  Filter,
  LayoutGrid,
  List,
  Quote,
  RefreshCw,
  Search,
  SortAsc,
  SortDesc,
} from "lucide-react";
import React, { useMemo, useState } from "react";
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
import { useCitations } from "@/hooks/useCitations";
import type { Citation, CitationsFilters } from "@/types/citations";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { CitationItem } from "./CitationItem";
import { CitedByItem } from "./CitedByItem";

interface CitationsSectionProps {
  documentId: string;
  className?: string;
}

export const CitationsSection: React.FC<CitationsSectionProps> = ({
  documentId,
  className = "",
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState<
    Citation["citationType"] | "all"
  >("all");
  const [sortBy, setSortBy] = useState<"date" | "title" | "year">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [viewMode, setViewMode] = useState<"card" | "compact">("card");
  const [activeTab, setActiveTab] = useState<"used" | "citedBy">("used");

  const filters: CitationsFilters = useMemo(
    () => ({
      search: searchTerm,
      citationType: selectedType === "all" ? undefined : selectedType,
      sortBy,
      sortOrder,
    }),
    [searchTerm, selectedType, sortBy, sortOrder],
  );

  const {
    data,
    isLoading,
    error,
    refetch,
    loadMoreCitationsUsed,
    loadMoreCitedBy,
    hasMoreCitationsUsed,
    hasMoreCitedBy,
    updateFilters,
  } = useCitations({
    documentId,
    filters,
    pageSize: 20,
  });

  // Update filters when local state changes
  React.useEffect(() => {
    updateFilters(filters);
  }, [filters, updateFilters]);

  const citationTypes: {
    value: Citation["citationType"] | "all";
    label: string;
  }[] = [
    { value: "all", label: "All Types" },
    { value: "journal", label: "Journal Articles" },
    { value: "book", label: "Books" },
    { value: "website", label: "Websites" },
    { value: "conference", label: "Conference Papers" },
    { value: "report", label: "Reports" },
    { value: "other", label: "Other" },
  ];

  const sortOptions = [
    { value: "date", label: "Date Added" },
    { value: "title", label: "Title" },
    { value: "year", label: "Publication Year" },
  ];

  const handleExportCitations = () => {
    if (!data?.citationsUsed.citations) return;

    const csvContent = [
      ["Title", "Authors", "Year", "Source", "Type", "DOI", "URL"].join(","),
      ...data.citationsUsed.citations.map((citation) =>
        [
          `"${citation.title}"`,
          `"${citation.authors.join("; ")}"`,
          citation.year,
          `"${citation.source}"`,
          citation.citationType,
          citation.doi || "",
          citation.url || "",
        ].join(","),
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `citations-${documentId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-destructive">
            Error Loading Citations
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={refetch} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BookMarked className="h-5 w-5" />
              Citations & References
            </CardTitle>
            <CardDescription>
              Citations used in this document and documents that cite this work
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCitations}
              disabled={!data?.citationsUsed.citations.length}
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={refetch}
              disabled={isLoading}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Filters and Controls */}
        <div className="space-y-4 mb-6">
          {/* Search and Type Filter */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search citations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={selectedType}
              onChange={(e) =>
                setSelectedType(
                  e.target.value as Citation["citationType"] | "all",
                )
              }
              className="px-3 py-2 border rounded-md bg-background min-w-[150px]"
            >
              {citationTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sort and View Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                value={sortBy}
                onChange={(e) =>
                  setSortBy(e.target.value as "date" | "title" | "year")
                }
                className="px-3 py-1 border rounded-md bg-background text-sm"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  setSortOrder(sortOrder === "asc" ? "desc" : "asc")
                }
              >
                {sortOrder === "asc" ? (
                  <SortAsc className="h-4 w-4" />
                ) : (
                  <SortDesc className="h-4 w-4" />
                )}
              </Button>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === "card" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("card")}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === "compact" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("compact")}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Tabs for Citations Used vs Cited By */}
        <Tabs
          value={activeTab}
          onValueChange={(value: string) =>
            setActiveTab(value as "used" | "citedBy")
          }
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="used" className="flex items-center gap-2">
              <Quote className="h-4 w-4" />
              Citations Used
              {data && (
                <Badge variant="secondary" className="ml-2">
                  {data.citationsUsed.total}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="citedBy" className="flex items-center gap-2">
              <BookMarked className="h-4 w-4" />
              Cited By
              {data && (
                <Badge variant="secondary" className="ml-2">
                  {data.citedBy.total}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>{" "}
          <TabsContent value="used" className="mt-6">
            {isLoading && !data ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }, (_, i) => `used-skeleton-${i}`).map(
                  (key) => (
                    <div key={key} className="animate-pulse">
                      <div className="h-32 bg-muted rounded-lg"></div>
                    </div>
                  ),
                )}
              </div>
            ) : data?.citationsUsed.citations.length ? (
              <div className="space-y-4">
                {data.citationsUsed.citations.map((citation, _index) => {
                  const docCitation = data.citationsUsed.documentCitations.find(
                    (dc) => dc.citationId === citation.id,
                  );
                  return (
                    <CitationItem
                      key={citation.id}
                      citation={citation}
                      documentCitation={docCitation}
                      showContext={true}
                      compact={viewMode === "compact"}
                    />
                  );
                })}

                {hasMoreCitationsUsed && (
                  <div className="flex justify-center pt-4">
                    <Button
                      variant="outline"
                      onClick={loadMoreCitationsUsed}
                      disabled={isLoading}
                    >
                      {isLoading ? "Loading..." : "Load More Citations"}
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Quote className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No citations found{searchTerm ? " for your search" : ""}.</p>
              </div>
            )}
          </TabsContent>{" "}
          <TabsContent value="citedBy" className="mt-6">
            {isLoading && !data ? (
              <div className="space-y-4">
                {Array.from(
                  { length: 3 },
                  (_, i) => `cited-by-skeleton-${i}`,
                ).map((key) => (
                  <div key={key} className="animate-pulse">
                    <div className="h-32 bg-muted rounded-lg"></div>
                  </div>
                ))}
              </div>
            ) : data?.citedBy.documents.length ? (
              <div className="space-y-4">
                {data.citedBy.documents.map((document) => (
                  <CitedByItem
                    key={document.id}
                    document={document}
                    compact={viewMode === "compact"}
                  />
                ))}

                {hasMoreCitedBy && (
                  <div className="flex justify-center pt-4">
                    <Button
                      variant="outline"
                      onClick={loadMoreCitedBy}
                      disabled={isLoading}
                    >
                      {isLoading ? "Loading..." : "Load More Documents"}
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <BookMarked className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>
                  No citing documents found
                  {searchTerm ? " for your search" : ""}.
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
