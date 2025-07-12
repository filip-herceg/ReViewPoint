import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StatusBadge, PriorityBadge, OverdueBadge } from '@/components/ui/status-badge';
import {
    FileText,
    Download,
    Calendar,
    User,
    Clock,
    CheckCircle,
    XCircle,
    Eye,
    ArrowLeft,
    Star,
    MessageSquare,
    ThumbsUp,
    ThumbsDown,
    AlertTriangle,
    Settings,
    Play,
    Package
} from 'lucide-react';
import { CitationsSection } from '@/components/citations/CitationsSection';
import { useMarketplace } from '@/hooks/useMarketplace';
import { ModuleConfigSidebar } from '@/components/modules/ModuleConfigSidebar';

const ReviewDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [configSidebarOpen, setConfigSidebarOpen] = useState(false);
    const [selectedModule, setSelectedModule] = useState<any>(null);
    const [runningModules, setRunningModules] = useState<Set<string>>(new Set());
    const [moduleResults, setModuleResults] = useState<Record<string, any>>({});

    // Get marketplace data for available modules
    const { userSubscriptions, isModuleSubscribed, getUserSubscription } = useMarketplace();

    // TODO: Replace with actual data from API
    const review = {
        id: id || '1',
        documentId: '1',
        documentName: 'Project Architecture.pdf',
        documentDescription: 'System architecture documentation for the new platform including microservices design, data flow diagrams, and deployment architecture.',
        status: 'pending',
        assignedTo: 'Current User',
        assignedAt: '2024-01-16T08:30:00Z',
        dueDate: '2024-01-20T23:59:59Z',
        priority: 'high',
        author: 'John Doe',
        authorEmail: 'john.doe@company.com',
        fileSize: '2.4 MB',
        fileType: 'pdf',
        downloadUrl: '/api/uploads/1/download',
        tags: ['architecture', 'documentation', 'microservices'],
        reviewGuidelines: [
            'Check for completeness of architectural components',
            'Verify scalability considerations',
            'Review security implications',
            'Assess maintainability and documentation quality'
        ]
    };

    const [reviewData, setReviewData] = useState({
        rating: 0,
        comments: '',
        suggestions: [''],
        decision: '' as 'approve' | 'reject' | 'request-changes' | ''
    });

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'bg-destructive/10 text-destructive';
            case 'medium': return 'bg-warning/10 text-warning-foreground';
            case 'low': return 'bg-success/10 text-success-foreground';
            default: return 'bg-muted text-muted-foreground';
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const isOverdue = (dueDateString: string) => {
        return new Date(dueDateString) < new Date();
    };

    const handleRatingClick = (rating: number) => {
        setReviewData(prev => ({ ...prev, rating }));
    };

    const addSuggestion = () => {
        setReviewData(prev => ({
            ...prev,
            suggestions: [...prev.suggestions, '']
        }));
    };

    const updateSuggestion = (index: number, value: string) => {
        setReviewData(prev => ({
            ...prev,
            suggestions: prev.suggestions.map((s, i) => i === index ? value : s)
        }));
    };

    const removeSuggestion = (index: number) => {
        setReviewData(prev => ({
            ...prev,
            suggestions: prev.suggestions.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (decision: 'approve' | 'reject' | 'request-changes') => {
        if (!reviewData.comments.trim()) {
            alert('Please provide comments for your review.');
            return;
        }

        if (reviewData.rating === 0) {
            alert('Please provide a rating for this document.');
            return;
        }

        setIsSubmitting(true);

        try {
            // TODO: Replace with actual API call
            await new Promise(resolve => setTimeout(resolve, 1000));

            console.log('Submitting review:', {
                ...reviewData,
                decision,
                suggestions: reviewData.suggestions.filter(s => s.trim())
            });

            navigate('/reviews');
        } catch (error) {
            console.error('Failed to submit review:', error);
            alert('Failed to submit review. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Configure module - opens the configuration sidebar
    const handleConfigureModule = (moduleId: string) => {
        const subscription = getUserSubscription(moduleId);
        if (subscription) {
            const module = userSubscriptions.find(s => s.moduleId === moduleId)?.module;
            if (module) {
                setSelectedModule({
                    id: module.id,
                    name: module.displayName || module.name,
                    version: module.currentVersion,
                    description: module.description,
                    configSchema: module.configuration || {},
                    userConfig: subscription.configuration || {},
                    defaultConfig: Object.keys(module.configuration || {}).reduce((acc, key) => {
                        acc[key] = module.configuration![key].default;
                        return acc;
                    }, {} as any)
                });
                setConfigSidebarOpen(true);
            }
        }
    };

    // Run module analysis - executes the module and simulates results
    const handleRunModule = async (moduleId: string) => {
        const subscription = getUserSubscription(moduleId);
        if (!subscription) return;

        const module = userSubscriptions.find(s => s.moduleId === moduleId)?.module;
        if (!module) return;

        // Add to running modules
        setRunningModules(prev => new Set([...prev, moduleId]));

        try {
            // Simulate module execution time
            await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));

            // Generate simulated results based on module type
            const simulatedResult = generateModuleResult(module, review);
            setModuleResults(prev => ({
                ...prev,
                [moduleId]: simulatedResult
            }));

            console.log(`Module ${module.name} completed analysis:`, simulatedResult);
        } catch (error) {
            console.error(`Module ${module.name} execution failed:`, error);
        } finally {
            // Remove from running modules
            setRunningModules(prev => {
                const newSet = new Set(prev);
                newSet.delete(moduleId);
                return newSet;
            });
        }
    };

    // Generate simulated module results
    const generateModuleResult = (module: any, reviewDoc: any) => {
        const results = {
            'plagiarism-detector': {
                status: 'completed',
                score: Math.round((Math.random() * 20 + 80) * 100) / 100, // 80-100%
                findings: Math.floor(Math.random() * 3), // 0-2 issues
                details: [
                    'Document appears to be original content',
                    'No significant plagiarism detected',
                    'Minor similarity found in standard terminology (acceptable)'
                ].slice(0, Math.floor(Math.random() * 3) + 1)
            },
            'citation-validator-pro': {
                status: 'completed',
                score: Math.round((Math.random() * 25 + 65) * 100) / 100, // 65-90%
                findings: Math.floor(Math.random() * 6) + 2, // 2-7 issues
                totalCitations: Math.floor(Math.random() * 15) + 12, // 12-26 citations
                validCitations: Math.floor(Math.random() * 8) + 8, // 8-15 valid
                issues: [
                    {
                        type: 'misrepresentation',
                        severity: 'high',
                        location: 'Page 3, Paragraph 2, Line 8-10',
                        citation: 'Smith et al. (2021)',
                        issue: 'The paper claims Smith et al. found "significant improvement in 95% of cases", but the source actually reports 73% improvement rate.',
                        recommendation: 'Correct the percentage or find additional supporting evidence'
                    },
                    {
                        type: 'missing_context',
                        severity: 'medium',
                        location: 'Page 5, Section 3.1, Line 15',
                        citation: 'Johnson & Brown (2020)',
                        issue: 'The citation is used to support a broad claim about "all manufacturing processes", but the source only studied automotive manufacturing.',
                        recommendation: 'Narrow the claim or cite additional sources covering other industries'
                    },
                    {
                        type: 'outdated_source',
                        severity: 'medium',
                        location: 'Page 7, Introduction, Line 3',
                        citation: 'Williams (1998)',
                        issue: 'Source is 27 years old in a rapidly evolving field. Current standards and practices may have changed significantly.',
                        recommendation: 'Find more recent sources (preferably within last 5-10 years) to support this claim'
                    },
                    {
                        type: 'unreliable_source',
                        severity: 'high',
                        location: 'Page 9, Discussion, Line 22',
                        citation: 'TechBlog.com (2023)',
                        issue: 'Source appears to be a commercial blog without peer review. Not appropriate for academic citation.',
                        recommendation: 'Replace with peer-reviewed academic source or industry report from reputable organization'
                    },
                    {
                        type: 'citation_not_found',
                        severity: 'high',
                        location: 'Page 4, Methodology, Line 12',
                        citation: 'Davis et al. (2022)',
                        issue: 'The cited work does not contain any information about the methodology being referenced.',
                        recommendation: 'Verify the citation is correct or find the appropriate source for this methodology'
                    },
                    {
                        type: 'format_error',
                        severity: 'low',
                        location: 'Page 6, References, Entry 12',
                        citation: 'Thompson, K. (2021)',
                        issue: 'Incomplete citation missing journal name, volume, and page numbers.',
                        recommendation: 'Complete the citation according to APA format requirements'
                    },
                    {
                        type: 'overcitation',
                        severity: 'low',
                        location: 'Page 8, Paragraph 3',
                        citation: 'Multiple (5 citations for single claim)',
                        issue: 'Five citations provided for a basic, well-established fact that requires minimal support.',
                        recommendation: 'Reduce to 1-2 most authoritative sources'
                    },
                    {
                        type: 'cherry_picking',
                        severity: 'medium',
                        location: 'Page 10, Results, Line 5-8',
                        citation: 'Anderson (2023)',
                        issue: 'Only favorable results from the source are cited, ignoring contradictory findings mentioned in the same paper.',
                        recommendation: 'Present a balanced view or acknowledge limitations mentioned in the source'
                    },
                    {
                        type: 'predatory_journal',
                        severity: 'high',
                        location: 'Page 11, Literature Review, Line 18',
                        citation: 'Martinez & Lee (2022) - Journal of Universal Science',
                        issue: 'Source appears to be from a predatory journal with questionable peer review standards.',
                        recommendation: 'Find equivalent research published in reputable, indexed journals'
                    },
                    {
                        type: 'broken_link',
                        severity: 'medium',
                        location: 'Page 12, References, Entry 8',
                        citation: 'World Health Organization (2021)',
                        issue: 'URL provided in citation returns 404 error. Document may have been moved or removed.',
                        recommendation: 'Find current URL or use alternative access method (DOI, archived version)'
                    }
                ].slice(0, Math.floor(Math.random() * 6) + 4), // Show 4-9 random issues
                recommendations: [
                    'Consider using citation management software to ensure consistent formatting',
                    'Prioritize peer-reviewed sources over blog posts and commercial websites',
                    'Verify all claims against the actual content of cited sources',
                    'Update outdated references where more recent research is available',
                    'Ensure citations directly support the specific claims being made'
                ]
            },
            'grammar-checker': {
                status: 'completed',
                score: Math.round((Math.random() * 30 + 70) * 100) / 100, // 70-100%
                findings: Math.floor(Math.random() * 8), // 0-7 issues
                issues: [
                    'Passive voice usage in paragraph 3',
                    'Missing comma in compound sentence (line 42)',
                    'Consider shorter sentences for clarity',
                    'Technical jargon could be simplified',
                    'Inconsistent terminology usage'
                ].slice(0, Math.floor(Math.random() * 5) + 1)
            },
            'fact-checker': {
                status: 'completed',
                score: Math.round((Math.random() * 25 + 75) * 100) / 100, // 75-100%
                findings: Math.floor(Math.random() * 4), // 0-3 issues
                claims: [
                    { claim: 'Statistical data in section 2', verified: Math.random() > 0.3 },
                    { claim: 'Historical references', verified: Math.random() > 0.2 },
                    { claim: 'Technical specifications', verified: Math.random() > 0.1 }
                ]
            },
            'bias-detector': {
                status: 'completed',
                score: Math.round((Math.random() * 20 + 80) * 100) / 100, // 80-100%
                findings: Math.floor(Math.random() * 3), // 0-2 issues
                biases: [
                    'Slight confirmation bias in argument structure',
                    'Neutral language maintained throughout',
                    'Balanced presentation of viewpoints'
                ].slice(0, Math.floor(Math.random() * 2) + 1)
            }
        };

        return (results as any)[module.id] || {
            status: 'completed',
            score: Math.round((Math.random() * 30 + 70) * 100) / 100,
            findings: Math.floor(Math.random() * 5),
            analysis: `Analysis completed for ${module.name}. Document reviewed successfully.`
        };
    };

    const handleSaveModuleConfig = async (config: any) => {
        console.log('Running module with config:', selectedModule?.id, config);
        
        // TODO: Implement actual module execution
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log('Module executed successfully');
        setConfigSidebarOpen(false);
    };

    const handleRevertConfig = () => {
        console.log('Reverting module configuration');
    };

    const handleResetToDefault = () => {
        console.log('Resetting module to default configuration');
    };

    // Get modules that can process this document type
    const getCompatibleModules = () => {
        return userSubscriptions.filter(subscription => {
            const module = subscription.module;
            // Check if module supports the file type and is active
            return subscription.status === 'active' && 
                   module.capabilities.supportedFormats.includes(review.fileType as any);
        });
    };

    const renderStarRating = () => {
        return (
            <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Rating:</span>
                <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }, (_, i) => (
                        <Button
                            key={i}
                            type="button"
                            variant="icon-sm"
                            size="icon-sm"
                            onClick={() => handleRatingClick(i + 1)}
                        >
                            <Star
                                className={`h-6 w-6 cursor-pointer transition-colors ${i < reviewData.rating
                                    ? 'text-yellow-400 fill-yellow-400'
                                    : 'text-gray-300 hover:text-yellow-300'
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
                                <CardTitle className="text-2xl">{review.documentName}</CardTitle>
                                <StatusBadge status={review.status} />
                                <PriorityBadge priority={review.priority} />
                                {review.dueDate && isOverdue(review.dueDate) && review.status !== 'completed' && (
                                    <OverdueBadge />
                                )}
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
                                <span className="font-medium">{formatDate(review.assignedAt)}</span>
                            </div>
                            {review.dueDate && (
                                <div className="flex items-center gap-2 text-sm">
                                    <Clock className="h-4 w-4 text-muted-foreground" />
                                    <span className="text-muted-foreground">Due date:</span>
                                    <span className={`font-medium ${isOverdue(review.dueDate) ? 'text-destructive' : ''}`}>
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
                            <li key={index} className="flex items-start gap-2">
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
                                        <div key={module.id} className="border rounded-lg p-4 space-y-3">
                                            <div className="flex items-start justify-between">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-2 bg-primary/10 rounded-lg">
                                                        <Package className="h-4 w-4 text-primary" />
                                                    </div>
                                                    <div>
                                                        <h4 className="font-medium">{module.displayName}</h4>
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
                                                Estimated time: ~{module.capabilities.estimatedProcessingTime}s
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
                                        const module = userSubscriptions.find(s => s.moduleId === moduleId)?.module;
                                        if (!module) return null;
                                        
                                        return (
                                            <Card key={moduleId} className="border-green-200 bg-green-50/50">
                                                <CardHeader className="pb-3">
                                                    <CardTitle className="text-base flex items-center gap-2">
                                                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                                                            {module.displayName || module.name}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-green-600 border-green-600">
                                                            {result.status}
                                                        </Badge>
                                                    </CardTitle>
                                                </CardHeader>
                                                <CardContent className="pt-0">
                                                    <div className="space-y-3">
                                                        {result.score && (
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-sm text-muted-foreground">Score:</span>
                                                                <Badge variant={result.score > 90 ? "default" : result.score > 70 ? "secondary" : "destructive"}>
                                                                    {result.score}%
                                                                </Badge>
                                                            </div>
                                                        )}
                                                        
                                                        {result.findings !== undefined && (
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-sm text-muted-foreground">Issues found:</span>
                                                                <Badge variant={result.findings === 0 ? "default" : "secondary"}>
                                                                    {result.findings}
                                                                </Badge>
                                                            </div>
                                                        )}
                                                        
                                                        {result.details && (
                                                            <div className="space-y-1">
                                                                <p className="text-sm font-medium">Details:</p>
                                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                                    {result.details.map((detail: string, idx: number) => (
                                                                        <li key={idx} className="flex items-start gap-2">
                                                                            <span className="w-1 h-1 bg-muted-foreground rounded-full mt-2 flex-shrink-0"></span>
                                                                            {detail}
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}
                                                        
                                                        {result.issues && Array.isArray(result.issues) && result.issues.length > 0 && typeof result.issues[0] === 'string' && (
                                                            <div className="space-y-1">
                                                                <p className="text-sm font-medium">Issues:</p>
                                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                                    {result.issues.map((issue: string, idx: number) => (
                                                                        <li key={idx} className="flex items-start gap-2">
                                                                            <span className="w-1 h-1 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></span>
                                                                            {issue}
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}
                                                        
                                                        {result.claims && (
                                                            <div className="space-y-1">
                                                                <p className="text-sm font-medium">Fact Checks:</p>
                                                                <div className="space-y-1">
                                                                    {result.claims.map((claim: any, idx: number) => (
                                                                        <div key={idx} className="flex items-center gap-2 text-sm">
                                                                            {claim.verified ? (
                                                                                <CheckCircle className="h-3 w-3 text-green-600" />
                                                                            ) : (
                                                                                <XCircle className="h-3 w-3 text-red-600" />
                                                                            )}
                                                                            <span className={claim.verified ? "text-green-700" : "text-red-700"}>
                                                                                {claim.claim}
                                                                            </span>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                        
                                                        {result.biases && (
                                                            <div className="space-y-1">
                                                                <p className="text-sm font-medium">Bias Analysis:</p>
                                                                <ul className="text-sm text-muted-foreground space-y-1">
                                                                    {result.biases.map((bias: string, idx: number) => (
                                                                        <li key={idx} className="flex items-start gap-2">
                                                                            <span className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                                                                            {bias}
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}
                                                        
                                                        {/* Citation Validator Pro specific results */}
                                                        {result.totalCitations && (
                                                            <div className="grid grid-cols-3 gap-4 p-3 bg-blue-50 rounded-lg">
                                                                <div className="text-center">
                                                                    <div className="text-lg font-semibold text-blue-900">{result.totalCitations}</div>
                                                                    <div className="text-xs text-blue-700">Total Citations</div>
                                                                </div>
                                                                <div className="text-center">
                                                                    <div className="text-lg font-semibold text-green-700">{result.validCitations}</div>
                                                                    <div className="text-xs text-green-600">Valid Citations</div>
                                                                </div>
                                                                <div className="text-center">
                                                                    <div className="text-lg font-semibold text-red-700">{result.totalCitations - result.validCitations}</div>
                                                                    <div className="text-xs text-red-600">Issues Found</div>
                                                                </div>
                                                            </div>
                                                        )}
                                                        
                                                        {result.issues && Array.isArray(result.issues) && result.issues.length > 0 && typeof result.issues[0] === 'object' && (
                                                            <div className="space-y-3">
                                                                <p className="text-sm font-medium">Citation Issues Found:</p>
                                                                <div className="space-y-3 max-h-96 overflow-y-auto">
                                                                    {result.issues.map((issue: any, idx: number) => (
                                                                        <div key={idx} className={`border rounded-lg p-3 ${
                                                                            issue.severity === 'high' ? 'border-red-300 bg-red-50' :
                                                                            issue.severity === 'medium' ? 'border-yellow-300 bg-yellow-50' :
                                                                            'border-blue-300 bg-blue-50'
                                                                        }`}>
                                                                            <div className="flex items-start justify-between mb-2">
                                                                                <div className="flex items-center gap-2">
                                                                                    <Badge variant={
                                                                                        issue.severity === 'high' ? 'destructive' :
                                                                                        issue.severity === 'medium' ? 'secondary' :
                                                                                        'outline'
                                                                                    }>
                                                                                        {issue.severity} priority
                                                                                    </Badge>
                                                                                    <Badge variant="outline" className="text-xs">
                                                                                        {issue.type.replace('_', ' ')}
                                                                                    </Badge>
                                                                                </div>
                                                                            </div>
                                                                            
                                                                            <div className="space-y-2 text-sm">
                                                                                <div>
                                                                                    <span className="font-medium text-gray-700">Location:</span>
                                                                                    <span className="ml-2 font-mono text-blue-700 bg-blue-100 px-2 py-1 rounded text-xs">
                                                                                        {issue.location}
                                                                                    </span>
                                                                                </div>
                                                                                
                                                                                <div>
                                                                                    <span className="font-medium text-gray-700">Citation:</span>
                                                                                    <span className="ml-2 italic text-purple-700">
                                                                                        {issue.citation}
                                                                                    </span>
                                                                                </div>
                                                                                
                                                                                <div>
                                                                                    <span className="font-medium text-gray-700">Issue:</span>
                                                                                    <p className="mt-1 text-gray-600">{issue.issue}</p>
                                                                                </div>
                                                                                
                                                                                <div className="bg-white p-2 rounded border-l-4 border-blue-400">
                                                                                    <span className="font-medium text-blue-700">Recommendation:</span>
                                                                                    <p className="mt-1 text-blue-600 text-sm">{issue.recommendation}</p>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                        
                                                        {result.recommendations && (
                                                            <div className="space-y-2">
                                                                <p className="text-sm font-medium">General Recommendations:</p>
                                                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                                                    <ul className="text-sm text-green-700 space-y-1">
                                                                        {result.recommendations.map((rec: string, idx: number) => (
                                                                            <li key={idx} className="flex items-start gap-2">
                                                                                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                                                                                {rec}
                                                                            </li>
                                                                        ))}
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
                                You don't have any active modules that can process {review.fileType.toUpperCase()} files.
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
            {(review.status === 'pending' || review.status === 'in-progress') && (
                <Card>
                    <CardHeader>
                        <CardTitle>Submit Your Review</CardTitle>
                        <CardDescription>
                            Provide your feedback and rating for this document
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* Rating */}
                        <div className="space-y-2">
                            {renderStarRating()}
                        </div>

                        {/* Comments */}
                        <div className="space-y-2">
                            <label htmlFor="comments" className="text-sm font-medium">Comments *</label>
                            <textarea
                                id="comments"
                                placeholder="Provide detailed feedback about the document..."
                                value={reviewData.comments}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                                    setReviewData(prev => ({ ...prev, comments: e.target.value }))
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
                                <label className="text-sm font-medium">Suggestions for Improvement</label>
                                <Button type="button" variant="outline" size="sm" onClick={addSuggestion}>
                                    Add Suggestion
                                </Button>
                            </div>
                            <div className="space-y-2">
                                {reviewData.suggestions.map((suggestion, index) => (
                                    <div key={index} className="flex items-center gap-2">
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
                                onClick={() => handleSubmit('approve')}
                                disabled={isSubmitting || !reviewData.comments.trim() || reviewData.rating === 0}
                                className="bg-success-foreground/90 hover:bg-success-foreground text-white"
                            >
                                <ThumbsUp className="h-4 w-4 mr-2" />
                                {isSubmitting ? 'Submitting...' : 'Approve'}
                            </Button>

                            <Button
                                onClick={() => handleSubmit('request-changes')}
                                disabled={isSubmitting || !reviewData.comments.trim() || reviewData.rating === 0}
                                variant="outline"
                                className="border-warning-foreground text-warning-foreground hover:bg-warning/10"
                            >
                                <AlertTriangle className="h-4 w-4 mr-2" />
                                {isSubmitting ? 'Submitting...' : 'Request Changes'}
                            </Button>

                            <Button
                                onClick={() => handleSubmit('reject')}
                                disabled={isSubmitting || !reviewData.comments.trim() || reviewData.rating === 0}
                                variant="outline"
                                className="border-destructive text-destructive hover:bg-destructive/10"
                            >
                                <ThumbsDown className="h-4 w-4 mr-2" />
                                {isSubmitting ? 'Submitting...' : 'Reject'}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Completed Review Display */}
            {review.status === 'completed' && (
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
                            <h3 className="text-lg font-semibold mb-2">Review Submitted Successfully</h3>
                            <p className="text-muted-foreground">
                                Your review has been submitted and the document author has been notified.
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
