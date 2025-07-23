import {
  AlertTriangle,
  ArrowLeft,
  Calendar,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Clock,
  Download,
  Eye,
  FileText,
  Filter,
  Package,
  Play,
  Settings,
  SortAsc,
  SortDesc,
  Star,
  ThumbsDown,
  ThumbsUp,
  User,
  XCircle,
} from "lucide-react";
import type React from "react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { CitationsSection } from "@/components/citations/CitationsSection";
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
import {
  OverdueBadge,
  PriorityBadge,
  StatusBadge,
} from "@/components/ui/status-badge";
import { useCitations } from "@/hooks/useCitations";
import { useMarketplace } from "@/hooks/useMarketplace";
import type { Module } from "@/types/marketplace";

// Citation issue types
interface CitationIssue {
  type: string;
  severity: "high" | "medium" | "low";
  location: string;
  citation: string;
  issue: string;
  recommendation: string;
}

// Citation issue sorting and filtering helpers
const getSeverityWeight = (severity: string) => {
  switch (severity) {
    case "high":
      return 3;
    case "medium":
      return 2;
    case "low":
      return 1;
    default:
      return 0;
  }
};

const parseLocation = (location: string) => {
  // Parse "Page 3, Paragraph 2, Line 8-10" format
  const pageMatch = location.match(/Page (\d+)/);
  const paragraphMatch = location.match(/Paragraph (\d+)/);
  const lineMatch = location.match(/Line (\d+)/);

  return {
    page: pageMatch ? parseInt(pageMatch[1]) : 0,
    paragraph: paragraphMatch ? parseInt(paragraphMatch[1]) : 0,
    line: lineMatch ? parseInt(lineMatch[1]) : 0,
  };
};

const sortIssues = (
  issues: CitationIssue[],
  sortBy: string,
  direction: "asc" | "desc",
) => {
  return [...issues].sort((a, b) => {
    let comparison = 0;

    if (sortBy === "severity") {
      comparison =
        getSeverityWeight(a.severity) - getSeverityWeight(b.severity);
    } else if (sortBy === "location") {
      const locA = parseLocation(a.location);
      const locB = parseLocation(b.location);

      comparison =
        locA.page - locB.page ||
        locA.paragraph - locB.paragraph ||
        locA.line - locB.line;
    }

    return direction === "desc" ? -comparison : comparison;
  });
};

const filterIssues = (
  issues: CitationIssue[],
  severityFilter: string,
  typeFilter: string,
) => {
  return issues.filter((issue) => {
    const severityMatch =
      severityFilter === "all" || issue.severity === severityFilter;
    const typeMatch = typeFilter === "all" || issue.type === typeFilter;
    return severityMatch && typeMatch;
  });
};

// Type for the module configuration sidebar
type ModuleConfigData = {
  id: string;
  name: string;
  version: string;
  description: string;
  configSchema?: Record<string, unknown>;
  defaultConfig?: Record<string, unknown>;
  userConfig?: Record<string, unknown>;
} | null;

// Module result types
interface ModuleResult {
  status: string;
  score?: number;
  findings?: number;
  totalCitations?: number;
  validCitations?: number;
  totalSources?: number;
  citationsAnalyzed?: number;
  citedByDocuments?: number;
  analysisDate?: string;
  coveragePercentage?: number;
  details?: string[];
  issues?: CitationIssue[];
  recommendations?: string[];
  analysis?: string;
  claims?: string[];
  biases?: string[];
}

const ReviewDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [configSidebarOpen, setConfigSidebarOpen] = useState(false);
  const [selectedModule, setSelectedModule] = useState<ModuleConfigData>(null);
  const [runningModules, setRunningModules] = useState<Set<string>>(new Set());
  const [moduleResults, setModuleResults] = useState<
    Record<string, ModuleResult>
  >({});

  // Citation Validator Pro UI state
  const [selectedIssue, setSelectedIssue] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<"location" | "severity">("severity");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [severityFilter, setSeverityFilter] = useState<
    "all" | "high" | "medium" | "low"
  >("all");
  const [typeFilter, setTypeFilter] = useState<"all" | string>("all");

  // Get marketplace data for available modules
  const { userSubscriptions, getUserSubscription } = useMarketplace();

  // TODO: Replace with actual data from API
  const review = {
    id: id || "1",
    documentId: "1",
    documentName: "Project Architecture.pdf",
    documentDescription:
      "System architecture documentation for the new platform including microservices design, data flow diagrams, and deployment architecture.",
    status: "pending",
    assignedTo: "Current User",
    assignedAt: "2024-01-16T08:30:00Z",
    dueDate: "2024-01-20T23:59:59Z",
    priority: "high",
    author: "John Doe",
    authorEmail: "john.doe@company.com",
    fileSize: "2.4 MB",
    fileType: "pdf",
    downloadUrl: "/api/uploads/1/download",
    tags: ["architecture", "documentation", "microservices"],
    reviewGuidelines: [
      "Check for completeness of architectural components",
      "Verify scalability considerations",
      "Review security implications",
      "Assess maintainability and documentation quality",
    ],
  };

  // Get citations data for realistic counts
  const { data: citationsData } = useCitations({
    documentId: review.documentId,
  });

  const [reviewData, setReviewData] = useState({
    rating: 0,
    comments: "",
    suggestions: [""],
    decision: "" as "approve" | "reject" | "request-changes" | "",
  });

  const _getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-destructive/10 text-destructive";
      case "medium":
        return "bg-warning/10 text-warning-foreground";
      case "low":
        return "bg-success/10 text-success-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const isOverdue = (dueDateString: string) => {
    return new Date(dueDateString) < new Date();
  };

  const handleRatingClick = (rating: number) => {
    setReviewData((prev) => ({ ...prev, rating }));
  };

  const addSuggestion = () => {
    setReviewData((prev) => ({
      ...prev,
      suggestions: [...prev.suggestions, ""],
    }));
  };

  const updateSuggestion = (index: number, value: string) => {
    setReviewData((prev) => ({
      ...prev,
      suggestions: prev.suggestions.map((s, i) => (i === index ? value : s)),
    }));
  };

  const removeSuggestion = (index: number) => {
    setReviewData((prev) => ({
      ...prev,
      suggestions: prev.suggestions.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (
    decision: "approve" | "reject" | "request-changes",
  ) => {
    if (!reviewData.comments.trim()) {
      alert("Please provide comments for your review.");
      return;
    }

    if (reviewData.rating === 0) {
      alert("Please provide a rating for this document.");
      return;
    }

    setIsSubmitting(true);

    try {
      // TODO: Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      console.log("Submitting review:", {
        ...reviewData,
        decision,
        suggestions: reviewData.suggestions.filter((s) => s.trim()),
      });

      navigate("/reviews");
    } catch (error) {
      console.error("Failed to submit review:", error);
      alert("Failed to submit review. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Configure module - opens the configuration sidebar
  const handleConfigureModule = (moduleId: string) => {
    const subscription = getUserSubscription(moduleId);
    if (subscription) {
      const module = userSubscriptions.find(
        (s) => s.moduleId === moduleId,
      )?.module;
      if (module) {
        setSelectedModule({
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
        });
        setConfigSidebarOpen(true);
      }
    }
  };

  // Run module analysis - executes the module and simulates results
  const handleRunModule = async (moduleId: string) => {
    const subscription = getUserSubscription(moduleId);
    if (!subscription) return;

    const module = userSubscriptions.find(
      (s) => s.moduleId === moduleId,
    )?.module;
    if (!module) return;

    // Add to running modules
    setRunningModules((prev) => new Set([...prev, moduleId]));

    try {
      // Simulate module execution time
      await new Promise((resolve) =>
        setTimeout(resolve, 2000 + Math.random() * 3000),
      );

      // Generate simulated results based on module type
      const simulatedResult = generateModuleResult(module, review);
      setModuleResults((prev) => ({
        ...prev,
        [moduleId]: simulatedResult,
      }));

      console.log(`Module ${module.name} completed analysis:`, simulatedResult);
    } catch (error) {
      console.error(`Module ${module.name} execution failed:`, error);
    } finally {
      // Remove from running modules
      setRunningModules((prev) => {
        const newSet = new Set(prev);
        newSet.delete(moduleId);
        return newSet;
      });
    }
  };

  // Generate simulated module results
  const generateModuleResult = (module: Module, _reviewDoc: unknown) => {
    // Get realistic citation counts from actual citations data
    const citationData = citationsData?.citationsUsed;
    const totalCitations =
      citationData?.total || Math.floor(Math.random() * 20) + 35; // Fallback to 35-54
    const uniqueSources =
      citationData?.items?.length || Math.floor(Math.random() * 15) + 15; // Fallback to 15-29
    const citedByCount =
      citationsData?.citedBy?.total || Math.floor(Math.random() * 30) + 15; // Fallback to 15-44

    const results = {
      "plagiarism-detector": {
        status: "completed",
        score: Math.round((Math.random() * 20 + 80) * 100) / 100, // 80-100%
        findings: Math.floor(Math.random() * 3), // 0-2 issues
        details: [
          "Document appears to be original content",
          "No significant plagiarism detected",
          "Minor similarity found in standard terminology (acceptable)",
        ].slice(0, Math.floor(Math.random() * 3) + 1),
      },
      "citation-validator-pro": {
        status: "completed",
        score: Math.round((Math.random() * 25 + 65) * 100) / 100, // 65-90%
        findings: 14, // Fixed 14 issues as requested
        // Use realistic citation count from actual citations data (total citation instances, not sources)
        totalCitations: totalCitations, // This is now the actual number of citations in the paper
        validCitations: totalCitations - 14, // Total - issues found = valid citations
        // Additional metadata about citation analysis
        totalSources: uniqueSources, // Number of unique sources
        citationsAnalyzed: totalCitations,
        citedByDocuments: citedByCount, // From "Cited By" tab
        analysisDate: new Date().toISOString(),
        coveragePercentage: Math.round(
          (totalCitations / (totalCitations + 5)) * 100,
        ), // Assuming some citations might be missed
        issues: [
          {
            type: "misrepresentation",
            severity: "high",
            location: "Page 2, Section 1.2, Line 15-17",
            citation: "Fowler & Lewis (2014)",
            issue:
              'The document claims Fowler & Lewis recommend "always using microservices for all applications", but the source advocates for careful consideration and warns against microservices complexity for simple applications.',
            recommendation:
              "Correct the interpretation to reflect the nuanced guidance in the original source",
          },
          {
            type: "missing_context",
            severity: "medium",
            location: "Page 4, Section 2.1, Line 8",
            citation: "Newman (2015)",
            issue:
              "The citation supports container orchestration benefits but ignores the operational complexity concerns discussed in the same chapter.",
            recommendation:
              "Include both benefits and challenges mentioned in the source for balanced perspective",
          },
          {
            type: "outdated_source",
            severity: "high",
            location: "Page 3, Architecture Overview, Line 22",
            citation: "Docker Documentation (2016)",
            issue:
              "Docker documentation from 2016 is outdated for current containerization best practices. Many security and performance recommendations have changed.",
            recommendation:
              "Update to current Docker documentation or recent container security guides",
          },
          {
            type: "unreliable_source",
            severity: "high",
            location: "Page 7, Performance Analysis, Line 33",
            citation: "TechCrunch Article (2023)",
            issue:
              "TechCrunch is a news publication, not an authoritative source for technical architecture decisions. Lacks peer review and technical depth.",
            recommendation:
              "Replace with academic research, technical white papers, or industry benchmark studies",
          },
          {
            type: "citation_not_found",
            severity: "high",
            location: "Page 5, Database Design, Line 19",
            citation: "PostgreSQL Performance Tuning Guide (2022)",
            issue:
              "The cited performance optimization techniques do not appear in the referenced PostgreSQL documentation.",
            recommendation:
              "Verify the source or find the correct PostgreSQL performance documentation",
          },
          {
            type: "format_error",
            severity: "low",
            location: "Page 9, References, Entry 15",
            citation: "Kubernetes Official Docs",
            issue:
              "Incomplete citation missing specific page, version, and access date for web documentation.",
            recommendation:
              "Include full URL, version number, and access date for web resources",
          },
          {
            type: "overcitation",
            severity: "low",
            location: "Page 6, Section 3.2, Paragraph 1",
            citation: "Multiple (6 citations for REST principles)",
            issue:
              "Six citations provided for basic REST architectural principles that are well-established.",
            recommendation:
              "Reduce to 1-2 authoritative sources like Fielding's original dissertation",
          },
          {
            type: "cherry_picking",
            severity: "medium",
            location: "Page 8, Scalability Section, Line 12-15",
            citation: "AWS Architecture Center (2023)",
            issue:
              "Only positive scalability metrics cited while ignoring cost implications and complexity warnings in the same AWS documentation.",
            recommendation:
              "Present complete picture including trade-offs mentioned in the source",
          },
          {
            type: "predatory_journal",
            severity: "medium",
            location: "Page 10, Security Patterns, Line 28",
            citation: "International Journal of Computer Science (2022)",
            issue:
              "This journal has questionable peer review standards and is not indexed in major academic databases.",
            recommendation:
              "Replace with security research from reputable conferences like IEEE S&P or ACM CCS",
          },
          {
            type: "broken_link",
            severity: "medium",
            location: "Page 11, References, Entry 23",
            citation: "Microsoft Azure Architecture Patterns (2021)",
            issue:
              "URL provided returns 404 error. Microsoft may have restructured their documentation.",
            recommendation:
              "Find current Azure architecture documentation or use archived version",
          },
          {
            type: "version_mismatch",
            severity: "medium",
            location: "Page 12, Implementation Guide, Line 5",
            citation: "Spring Boot Reference (2019)",
            issue:
              "Citing Spring Boot 2.1 documentation while project appears to use Spring Boot 3.x features.",
            recommendation:
              "Update citation to match the Spring Boot version actually being used",
          },
          {
            type: "scope_mismatch",
            severity: "medium",
            location: "Page 13, Monitoring Strategy, Line 18",
            citation: "Prometheus Monitoring (Small Scale Deployments)",
            issue:
              "Source discusses monitoring for small-scale deployments but is used to support enterprise-scale architecture decisions.",
            recommendation:
              "Find monitoring guidance appropriate for enterprise-scale microservices",
          },
          {
            type: "conflicting_sources",
            severity: "low",
            location: "Page 14, API Gateway Pattern, Line 7-10",
            citation: "Richardson (2018) vs Kong Documentation (2023)",
            issue:
              "Two sources provide contradictory recommendations about API gateway placement without acknowledging the conflict.",
            recommendation:
              "Acknowledge conflicting approaches and explain chosen rationale",
          },
          {
            type: "insufficient_evidence",
            severity: "medium",
            location: "Page 15, Technology Selection, Line 25",
            citation: "Single blog post (2023)",
            issue:
              "Critical technology choice (React vs Angular) supported by only one informal blog post.",
            recommendation:
              "Provide multiple comparative studies or formal evaluation criteria",
          },
        ],
        recommendations: [
          "Consider using citation management software to ensure consistent formatting",
          "Prioritize peer-reviewed sources over blog posts and commercial websites",
          "Verify all claims against the actual content of cited sources",
          "Update outdated references where more recent research is available",
          "Ensure citations directly support the specific claims being made",
        ],
      },
      "grammar-checker": {
        status: "completed",
        score: Math.round((Math.random() * 30 + 70) * 100) / 100, // 70-100%
        findings: Math.floor(Math.random() * 8), // 0-7 issues
        issues: [
          "Passive voice usage in paragraph 3",
          "Missing comma in compound sentence (line 42)",
          "Consider shorter sentences for clarity",
          "Technical jargon could be simplified",
          "Inconsistent terminology usage",
        ].slice(0, Math.floor(Math.random() * 5) + 1),
      },
      "fact-checker": {
        status: "completed",
        score: Math.round((Math.random() * 25 + 75) * 100) / 100, // 75-100%
        findings: Math.floor(Math.random() * 4), // 0-3 issues
        claims: [
          {
            claim: "Statistical data in section 2",
            verified: Math.random() > 0.3,
          },
          { claim: "Historical references", verified: Math.random() > 0.2 },
          { claim: "Technical specifications", verified: Math.random() > 0.1 },
        ],
      },
      "bias-detector": {
        status: "completed",
        score: Math.round((Math.random() * 20 + 80) * 100) / 100, // 80-100%
        findings: Math.floor(Math.random() * 3), // 0-2 issues
        biases: [
          "Slight confirmation bias in argument structure",
          "Neutral language maintained throughout",
          "Balanced presentation of viewpoints",
        ].slice(0, Math.floor(Math.random() * 2) + 1),
      },
    };

    return (
      (results as any)[module.id] || {
        status: "completed",
        score: Math.round((Math.random() * 30 + 70) * 100) / 100,
        findings: Math.floor(Math.random() * 5),
        analysis: `Analysis completed for ${module.name}. Document reviewed successfully.`,
      }
    );
  };

  const handleSaveModuleConfig = async (config: any) => {
    console.log("Running module with config:", selectedModule?.id, config);

    // TODO: Implement actual module execution
    await new Promise((resolve) => setTimeout(resolve, 1000));

    console.log("Module executed successfully");
    setConfigSidebarOpen(false);
  };

  const handleRevertConfig = () => {
    console.log("Reverting module configuration");
  };

  const handleResetToDefault = () => {
    console.log("Resetting module to default configuration");
  };

  // Get modules that can process this document type
  const getCompatibleModules = () => {
    return userSubscriptions.filter((subscription) => {
      const module = subscription.module;
      // Check if module supports the file type and is active
      return (
        subscription.status === "active" &&
        module.capabilities.supportedFormats.includes(review.fileType as any)
      );
    });
  };

  const renderStarRating = () => {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Rating:</span>
        <div className="flex items-center gap-1">
          {Array.from({ length: 5 }, (_, i) => (
            <Button
              key={`rating-star-${i + 1}`}
              type="button"
              variant="icon-sm"
              size="icon-sm"
              onClick={() => handleRatingClick(i + 1)}
            >
              <Star
                className={`h-6 w-6 cursor-pointer transition-colors ${
                  i < reviewData.rating
                    ? "text-yellow-400 fill-yellow-400"
                    : "text-gray-300 hover:text-yellow-300"
                }`}
              />
            </Button>
          ))}
        </div>
        <span className="text-sm text-muted-foreground">
          ({reviewData.rating}/5)
        </span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/reviews">
            <span className="flex items-center">
              <ArrowLeft className="h-4 w-4 mr-2" />
              <span>Back to Reviews</span>
            </span>
          </Link>
        </Button>
      </div>

      {/* Document Info */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <CardTitle className="text-2xl">
                  {review.documentName}
                </CardTitle>
                <StatusBadge status={review.status} />
                <PriorityBadge priority={review.priority} />
                {review.dueDate &&
                  isOverdue(review.dueDate) &&
                  review.status !== "completed" && <OverdueBadge />}
              </div>
              <CardDescription className="text-base">
                {review.documentDescription}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" asChild>
                <Link to={`/uploads/${review.documentId}`}>
                  <span className="flex items-center">
                    <Eye className="h-4 w-4 mr-2" />
                    <span>View Document</span>
                  </span>
                </Link>
              </Button>
              <Button size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Author:</span>
                <span className="font-medium">{review.author}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Assigned:</span>
                <span className="font-medium">
                  {formatDate(review.assignedAt)}
                </span>
              </div>
              {review.dueDate && (
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Due date:</span>
                  <span
                    className={`font-medium ${isOverdue(review.dueDate) ? "text-destructive" : ""}`}
                  >
                    {formatDate(review.dueDate)}
                  </span>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">File size:</span>
                <span className="font-medium">{review.fileSize}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">File type:</span>
                <span className="font-medium uppercase">{review.fileType}</span>
              </div>
            </div>
          </div>

          <hr className="my-4" />

          <div className="space-y-2">
            <h4 className="font-medium">Tags</h4>
            <div className="flex items-center gap-2">
              {review.tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Review Guidelines */}
      <Card>
        <CardHeader>
          <CardTitle>Review Guidelines</CardTitle>
          <CardDescription>
            Please consider the following aspects when reviewing this document
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {review.reviewGuidelines.map((guideline, index) => (
              <li
                key={`guideline-${guideline.slice(0, 20)}-${index}`}
                className="flex items-start gap-2"
              >
                <CheckCircle className="h-4 w-4 text-success-foreground mt-0.5 flex-shrink-0" />
                <span className="text-sm">{guideline}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Management - Run Modules */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Document Management
          </CardTitle>
          <CardDescription>
            Run analysis modules on this document to get additional insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          {getCompatibleModules().length > 0 ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {getCompatibleModules().map((subscription) => {
                  const module = subscription.module;
                  return (
                    <div
                      key={module.id}
                      className="border rounded-lg p-4 space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-primary/10 rounded-lg">
                            <Package className="h-4 w-4 text-primary" />
                          </div>
                          <div>
                            <h4 className="font-medium">
                              {module.displayName}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {module.description}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleRunModule(module.id)}
                          disabled={runningModules.has(module.id)}
                          className="flex-1"
                        >
                          {runningModules.has(module.id) ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                              Running...
                            </>
                          ) : (
                            <>
                              <Play className="h-4 w-4 mr-2" />
                              Run Analysis
                            </>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleConfigureModule(module.id)}
                          title="Configure module settings"
                        >
                          <Settings className="h-4 w-4" />
                        </Button>
                      </div>

                      <div className="text-xs text-muted-foreground">
                        Estimated time: ~
                        {module.capabilities.estimatedProcessingTime}s
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Module Results Section */}
              {Object.keys(moduleResults).length > 0 && (
                <div className="space-y-4 mt-6">
                  <h4 className="font-medium flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    Analysis Results
                  </h4>
                  {Object.entries(moduleResults).map(([moduleId, result]) => {
                    const module = userSubscriptions.find(
                      (s) => s.moduleId === moduleId,
                    )?.module;
                    if (!module) return null;

                    return (
                      <Card
                        key={moduleId}
                        className="border-green-200 bg-green-50/50"
                      >
                        <CardHeader className="pb-3">
                          <CardTitle className="text-base flex items-center gap-2">
                            <Badge
                              variant="secondary"
                              className="bg-green-100 text-green-800"
                            >
                              {module.displayName || module.name}
                            </Badge>
                            <Badge
                              variant="outline"
                              className="text-green-600 border-green-600"
                            >
                              {result.status}
                            </Badge>
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <div className="space-y-3">
                            {result.score && (
                              <div className="flex items-center gap-2">
                                <span className="text-sm text-muted-foreground">
                                  Score:
                                </span>
                                <Badge
                                  variant={
                                    result.score > 90
                                      ? "default"
                                      : result.score > 70
                                        ? "secondary"
                                        : "destructive"
                                  }
                                >
                                  {result.score}%
                                </Badge>
                              </div>
                            )}

                            {result.findings !== undefined && (
                              <div className="flex items-center gap-2">
                                <span className="text-sm text-muted-foreground">
                                  Issues found:
                                </span>
                                <Badge
                                  variant={
                                    result.findings === 0
                                      ? "default"
                                      : "secondary"
                                  }
                                >
                                  {result.findings}
                                </Badge>
                              </div>
                            )}

                            {result.details && (
                              <div className="space-y-1">
                                <p className="text-sm font-medium">Details:</p>
                                <ul className="text-sm text-muted-foreground space-y-1">
                                  {result.details.map(
                                    (detail: string, idx: number) => (
                                      <li
                                        key={`detail-${idx}-${detail.slice(0, 15)}`}
                                        className="flex items-start gap-2"
                                      >
                                        <span className="w-1 h-1 bg-muted-foreground rounded-full mt-2 flex-shrink-0"></span>
                                        {detail}
                                      </li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}

                            {result.issues &&
                              Array.isArray(result.issues) &&
                              result.issues.length > 0 &&
                              typeof result.issues[0] === "string" && (
                                <div className="space-y-1">
                                  <p className="text-sm font-medium">Issues:</p>
                                  <ul className="text-sm text-muted-foreground space-y-1">
                                    {result.issues.map(
                                      (issue: string, idx: number) => (
                                        <li
                                          key={`issue-${idx}-${issue.slice(0, 15)}`}
                                          className="flex items-start gap-2"
                                        >
                                          <span className="w-1 h-1 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></span>
                                          {issue}
                                        </li>
                                      ),
                                    )}
                                  </ul>
                                </div>
                              )}

                            {result.claims && (
                              <div className="space-y-1">
                                <p className="text-sm font-medium">
                                  Fact Checks:
                                </p>
                                <div className="space-y-1">
                                  {result.claims.map(
                                    (claim: any, idx: number) => (
                                      <div
                                        key={`claim-${idx}-${claim.claim?.slice(0, 15) || idx}`}
                                        className="flex items-center gap-2 text-sm"
                                      >
                                        {claim.verified ? (
                                          <CheckCircle className="h-3 w-3 text-green-600" />
                                        ) : (
                                          <XCircle className="h-3 w-3 text-red-600" />
                                        )}
                                        <span
                                          className={
                                            claim.verified
                                              ? "text-green-700"
                                              : "text-red-700"
                                          }
                                        >
                                          {claim.claim}
                                        </span>
                                      </div>
                                    ),
                                  )}
                                </div>
                              </div>
                            )}

                            {result.biases && (
                              <div className="space-y-1">
                                <p className="text-sm font-medium">
                                  Bias Analysis:
                                </p>
                                <ul className="text-sm text-muted-foreground space-y-1">
                                  {result.biases.map(
                                    (bias: string, idx: number) => (
                                      <li
                                        key={`bias-${idx}-${bias.slice(0, 15)}`}
                                        className="flex items-start gap-2"
                                      >
                                        <span className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                                        {bias}
                                      </li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}

                            {/* Citation Validator Pro specific results */}
                            {result.totalCitations && (
                              <div className="space-y-4">
                                {/* Summary Stats */}
                                <div className="grid grid-cols-3 gap-4 p-3 bg-blue-50 rounded-lg">
                                  <div className="text-center">
                                    <div className="text-lg font-semibold text-blue-900">
                                      {result.totalCitations}
                                    </div>
                                    <div className="text-xs text-blue-700">
                                      Total Citations
                                    </div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-lg font-semibold text-green-700">
                                      {result.validCitations}
                                    </div>
                                    <div className="text-xs text-green-600">
                                      Valid Citations
                                    </div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-lg font-semibold text-red-700">
                                      {result.totalCitations -
                                        result.validCitations}
                                    </div>
                                    <div className="text-xs text-red-600">
                                      Issues Found
                                    </div>
                                  </div>
                                </div>

                                {/* Controls */}
                                <div className="flex flex-wrap gap-2 items-center">
                                  <div className="flex items-center gap-2">
                                    <Filter className="h-4 w-4 text-gray-500" />
                                    <select
                                      value={severityFilter}
                                      onChange={(e) =>
                                        setSeverityFilter(e.target.value as any)
                                      }
                                      className="px-2 py-1 border rounded text-sm"
                                    >
                                      <option value="all">
                                        All Severities
                                      </option>
                                      <option value="high">
                                        High Priority
                                      </option>
                                      <option value="medium">
                                        Medium Priority
                                      </option>
                                      <option value="low">Low Priority</option>
                                    </select>
                                  </div>

                                  <select
                                    value={typeFilter}
                                    onChange={(e) =>
                                      setTypeFilter(e.target.value)
                                    }
                                    className="px-2 py-1 border rounded text-sm"
                                  >
                                    <option value="all">All Types</option>
                                    <option value="misrepresentation">
                                      Misrepresentation
                                    </option>
                                    <option value="missing_context">
                                      Missing Context
                                    </option>
                                    <option value="outdated_source">
                                      Outdated Source
                                    </option>
                                    <option value="unreliable_source">
                                      Unreliable Source
                                    </option>
                                    <option value="citation_not_found">
                                      Citation Not Found
                                    </option>
                                    <option value="format_error">
                                      Format Error
                                    </option>
                                    <option value="overcitation">
                                      Over Citation
                                    </option>
                                    <option value="cherry_picking">
                                      Cherry Picking
                                    </option>
                                    <option value="predatory_journal">
                                      Predatory Journal
                                    </option>
                                    <option value="broken_link">
                                      Broken Link
                                    </option>
                                  </select>

                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      if (sortBy === "severity") {
                                        setSortDirection(
                                          sortDirection === "asc"
                                            ? "desc"
                                            : "asc",
                                        );
                                      } else {
                                        setSortBy("severity");
                                        setSortDirection("desc");
                                      }
                                    }}
                                    className="flex items-center gap-1"
                                  >
                                    {sortBy === "severity" &&
                                    sortDirection === "desc" ? (
                                      <SortDesc className="h-3 w-3" />
                                    ) : (
                                      <SortAsc className="h-3 w-3" />
                                    )}
                                    Severity
                                  </Button>

                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      if (sortBy === "location") {
                                        setSortDirection(
                                          sortDirection === "asc"
                                            ? "desc"
                                            : "asc",
                                        );
                                      } else {
                                        setSortBy("location");
                                        setSortDirection("asc");
                                      }
                                    }}
                                    className="flex items-center gap-1"
                                  >
                                    {sortBy === "location" &&
                                    sortDirection === "desc" ? (
                                      <SortDesc className="h-3 w-3" />
                                    ) : (
                                      <SortAsc className="h-3 w-3" />
                                    )}
                                    Location
                                  </Button>
                                </div>

                                {/* Two-column layout */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                  {/* Left: Issue Navigator */}
                                  <div className="space-y-2">
                                    <h4 className="font-medium text-sm text-gray-700">
                                      Issues Navigator
                                    </h4>
                                    <div className="max-h-96 overflow-y-auto border rounded-lg bg-gray-50">
                                      {result.issues &&
                                        Array.isArray(result.issues) &&
                                        filterIssues(
                                          sortIssues(
                                            result.issues,
                                            sortBy,
                                            sortDirection,
                                          ),
                                          severityFilter,
                                          typeFilter,
                                        ).map((issue: any, _idx: number) => {
                                          const originalIdx =
                                            result.issues.indexOf(issue);
                                          return (
                                            <Button
                                              type="button"
                                              variant="ghost"
                                              key={`issue-button-${originalIdx}-${issue.type || "unknown"}`}
                                              onClick={() =>
                                                setSelectedIssue(
                                                  selectedIssue === originalIdx
                                                    ? null
                                                    : originalIdx,
                                                )
                                              }
                                              className={`w-full text-left p-3 border-b hover:bg-white transition-colors justify-start h-auto ${
                                                selectedIssue === originalIdx
                                                  ? "bg-white border-l-4 border-l-blue-500"
                                                  : ""
                                              }`}
                                            >
                                              <div className="flex items-center justify-between mb-1">
                                                <div className="flex items-center gap-2">
                                                  <Badge
                                                    variant={
                                                      issue.severity === "high"
                                                        ? "destructive"
                                                        : issue.severity ===
                                                            "medium"
                                                          ? "warning"
                                                          : "secondary"
                                                    }
                                                    className="text-xs"
                                                  >
                                                    {issue.severity}
                                                  </Badge>
                                                  {selectedIssue ===
                                                  originalIdx ? (
                                                    <ChevronDown className="h-3 w-3 text-gray-400" />
                                                  ) : (
                                                    <ChevronRight className="h-3 w-3 text-gray-400" />
                                                  )}
                                                </div>
                                              </div>
                                              <div className="text-xs text-gray-600 font-mono mb-1">
                                                {issue.location}
                                              </div>
                                              <div className="text-sm font-medium text-gray-800 truncate">
                                                {issue.type
                                                  .replace(/_/g, " ")
                                                  .replace(
                                                    /\b\w/g,
                                                    (l: string) =>
                                                      l.toUpperCase(),
                                                  )}
                                              </div>
                                              <div className="text-xs text-gray-500 italic truncate mt-1">
                                                {issue.citation}
                                              </div>
                                            </Button>
                                          );
                                        })}
                                    </div>
                                  </div>

                                  {/* Right: Issue Details */}
                                  <div className="space-y-2">
                                    <h4 className="font-medium text-sm text-gray-700">
                                      Issue Details
                                    </h4>
                                    <div className="border rounded-lg bg-white min-h-96">
                                      {selectedIssue !== null &&
                                      result.issues[selectedIssue] ? (
                                        <div className="p-4 space-y-4">
                                          <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-2">
                                              <Badge
                                                variant={
                                                  result.issues[selectedIssue]
                                                    .severity === "high"
                                                    ? "destructive"
                                                    : result.issues[
                                                          selectedIssue
                                                        ].severity === "medium"
                                                      ? "warning"
                                                      : "secondary"
                                                }
                                              >
                                                {
                                                  result.issues[selectedIssue]
                                                    .severity
                                                }{" "}
                                                priority
                                              </Badge>
                                              <Badge
                                                variant="outline"
                                                className="text-xs"
                                              >
                                                {result.issues[
                                                  selectedIssue
                                                ].type.replace(/_/g, " ")}
                                              </Badge>
                                            </div>
                                          </div>

                                          <div className="space-y-3 text-sm">
                                            <div>
                                              <span className="font-medium text-gray-700">
                                                Location:
                                              </span>
                                              <span className="ml-2 font-mono text-blue-700 bg-blue-100 px-2 py-1 rounded text-xs">
                                                {
                                                  result.issues[selectedIssue]
                                                    .location
                                                }
                                              </span>
                                            </div>

                                            <div>
                                              <span className="font-medium text-gray-700">
                                                Citation:
                                              </span>
                                              <div className="mt-1 italic text-purple-700 bg-purple-50 p-2 rounded">
                                                {
                                                  result.issues[selectedIssue]
                                                    .citation
                                                }
                                              </div>
                                            </div>

                                            <div>
                                              <span className="font-medium text-gray-700">
                                                Issue Description:
                                              </span>
                                              <div className="mt-1 text-gray-600 leading-relaxed">
                                                {
                                                  result.issues[selectedIssue]
                                                    .issue
                                                }
                                              </div>
                                            </div>

                                            <div className="bg-blue-50 p-3 rounded border-l-4 border-blue-400">
                                              <span className="font-medium text-blue-700">
                                                Recommendation:
                                              </span>
                                              <div className="mt-1 text-blue-600 text-sm leading-relaxed">
                                                {
                                                  result.issues[selectedIssue]
                                                    .recommendation
                                                }
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      ) : (
                                        <div className="p-8 text-center text-gray-500">
                                          <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                                          <p className="text-sm">
                                            Select an issue from the navigator
                                            to view details
                                          </p>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {result.recommendations && (
                              <div className="space-y-2">
                                <p className="text-sm font-medium">
                                  General Recommendations:
                                </p>
                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                  <ul className="text-sm text-green-700 space-y-1">
                                    {result.recommendations.map(
                                      (rec: string, idx: number) => (
                                        <li
                                          key={`recommendation-${idx}-${rec.slice(0, 15)}`}
                                          className="flex items-start gap-2"
                                        >
                                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                                          {rec}
                                        </li>
                                      ),
                                    )}
                                  </ul>
                                </div>
                              </div>
                            )}

                            {result.analysis && (
                              <div className="text-sm text-muted-foreground bg-white p-3 rounded border">
                                {result.analysis}
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <div className="text-sm text-blue-700">
                    <p className="font-medium">Running modules will:</p>
                    <ul className="mt-1 list-disc list-inside space-y-1">
                      <li>Process the document with selected analysis tools</li>
                      <li>Generate additional insights and reports</li>
                      <li>Add results to your review for consideration</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="font-medium text-muted-foreground mb-2">
                No Compatible Modules
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                You don't have any active modules that can process{" "}
                {review.fileType.toUpperCase()} files.
              </p>
              <Button variant="outline" asChild>
                <Link to="/marketplace">
                  <Package className="h-4 w-4 mr-2" />
                  Browse Marketplace
                </Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Review Form */}
      {(review.status === "pending" || review.status === "in-progress") && (
        <Card>
          <CardHeader>
            <CardTitle>Submit Your Review</CardTitle>
            <CardDescription>
              Provide your feedback and rating for this document
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Rating */}
            <div className="space-y-2">{renderStarRating()}</div>

            {/* Comments */}
            <div className="space-y-2">
              <label htmlFor="comments" className="text-sm font-medium">
                Comments *
              </label>
              <textarea
                id="comments"
                placeholder="Provide detailed feedback about the document..."
                value={reviewData.comments}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setReviewData((prev) => ({
                    ...prev,
                    comments: e.target.value,
                  }))
                }
                disabled={isSubmitting}
                rows={6}
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
            </div>

            {/* Suggestions */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  Suggestions for Improvement
                </span>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addSuggestion}
                >
                  Add Suggestion
                </Button>
              </div>
              <div className="space-y-2">
                {reviewData.suggestions.map((suggestion, index) => (
                  <div
                    key={`suggestion-${index}-${suggestion.slice(0, 10)}`}
                    className="flex items-center gap-2"
                  >
                    <input
                      type="text"
                      placeholder={`Suggestion ${index + 1}...`}
                      value={suggestion}
                      onChange={(e) => updateSuggestion(index, e.target.value)}
                      disabled={isSubmitting}
                      className="flex-1 px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                    {reviewData.suggestions.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeSuggestion(index)}
                        disabled={isSubmitting}
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Decision Buttons */}
            <div className="flex items-center gap-4 pt-4 border-t border-border">
              <Button
                onClick={() => handleSubmit("approve")}
                disabled={
                  isSubmitting ||
                  !reviewData.comments.trim() ||
                  reviewData.rating === 0
                }
                className="bg-success-foreground/90 hover:bg-success-foreground text-white"
              >
                <ThumbsUp className="h-4 w-4 mr-2" />
                {isSubmitting ? "Submitting..." : "Approve"}
              </Button>

              <Button
                onClick={() => handleSubmit("request-changes")}
                disabled={
                  isSubmitting ||
                  !reviewData.comments.trim() ||
                  reviewData.rating === 0
                }
                variant="outline"
                className="border-warning-foreground text-warning-foreground hover:bg-warning/10"
              >
                <AlertTriangle className="h-4 w-4 mr-2" />
                {isSubmitting ? "Submitting..." : "Request Changes"}
              </Button>

              <Button
                onClick={() => handleSubmit("reject")}
                disabled={
                  isSubmitting ||
                  !reviewData.comments.trim() ||
                  reviewData.rating === 0
                }
                variant="outline"
                className="border-destructive text-destructive hover:bg-destructive/10"
              >
                <ThumbsDown className="h-4 w-4 mr-2" />
                {isSubmitting ? "Submitting..." : "Reject"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Completed Review Display */}
      {review.status === "completed" && (
        <Card>
          <CardHeader>
            <CardTitle>Review Completed</CardTitle>
            <CardDescription>
              This review has been completed and submitted
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 mx-auto text-success-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                Review Submitted Successfully
              </h3>
              <p className="text-muted-foreground">
                Your review has been submitted and the document author has been
                notified.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Citations Section - Always visible */}
      <CitationsSection documentId={review.documentId} />

      {/* Module Configuration Sidebar */}
      <ModuleConfigSidebar
        isOpen={configSidebarOpen}
        onClose={() => setConfigSidebarOpen(false)}
        module={selectedModule}
        onSave={handleSaveModuleConfig}
        onRevert={handleRevertConfig}
        onResetToDefault={handleResetToDefault}
      />
    </div>
  );
};

export default ReviewDetailPage;
