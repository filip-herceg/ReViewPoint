import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/ui/status-badge';
// import { Separator } from '@/components/ui/separator';
import {
    FileText,
    Download,
    Calendar,
    User,
    Clock,
    CheckCircle,
    XCircle,
    Eye,
    MessageSquare,
    ArrowLeft,
    Share2
} from 'lucide-react';
import { CitationsSection } from '@/components/citations/CitationsSection';

const UploadDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();

    // TODO: Replace with actual data from API
    const upload = {
        id: id || '1',
        name: 'Project Architecture.pdf',
        description: 'System architecture documentation for the new platform including microservices design, data flow diagrams, and deployment architecture.',
        status: 'in-review',
        uploadedAt: '2024-01-15T10:30:00Z',
        uploadedBy: 'John Doe',
        fileSize: '2.4 MB',
        fileType: 'pdf',
        downloadUrl: '/api/uploads/1/download',
        tags: ['architecture', 'documentation', 'microservices'],
        metadata: {
            checksum: 'sha256:a1b2c3d4e5f6...',
            originalName: 'project-architecture-v2.pdf',
            mimeType: 'application/pdf'
        }
    };

    const reviews = [
        {
            id: '1',
            reviewer: 'Alice Wilson',
            status: 'completed',
            rating: 4,
            comments: 'Overall good architecture design. However, I have some concerns about the scalability of the proposed microservices communication pattern.',
            reviewedAt: '2024-01-16T09:15:00Z',
            suggestions: [
                'Consider implementing circuit breaker pattern for service communication',
                'Add more details about data consistency strategies',
                'Include performance benchmarks for proposed architecture'
            ]
        },
        {
            id: '2',
            reviewer: 'Bob Johnson',
            status: 'in-progress',
            rating: null,
            comments: 'Currently reviewing the security aspects of the proposed architecture.',
            reviewedAt: '2024-01-16T14:30:00Z',
            suggestions: []
        }
    ];

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getRatingStars = (rating: number) => {
        return '★'.repeat(rating) + '☆'.repeat(5 - rating);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" asChild>
                    <Link to="/uploads">
                        <span className="flex items-center">
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            <span>Back to Uploads</span>
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
                                <CardTitle className="text-2xl">{upload.name}</CardTitle>
                                <StatusBadge status={upload.status} />
                            </div>
                            <CardDescription className="text-base">
                                {upload.description}
                            </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm">
                                <Share2 className="h-4 w-4 mr-2" />
                                Share
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
                                <span className="text-muted-foreground">Uploaded by:</span>
                                <span className="font-medium">{upload.uploadedBy}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Calendar className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Upload date:</span>
                                <span className="font-medium">{formatDate(upload.uploadedAt)}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <FileText className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">File size:</span>
                                <span className="font-medium">{upload.fileSize}</span>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                                <span className="text-muted-foreground">File type:</span>
                                <span className="font-medium uppercase">{upload.fileType}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Reviews:</span>
                                <span className="font-medium">{reviews.length}</span>
                            </div>
                        </div>
                    </div>

                    <hr className="my-4" />

                    <div className="space-y-2">
                        <h4 className="font-medium">Tags</h4>
                        <div className="flex items-center gap-2">
                            {upload.tags.map((tag) => (
                                <Badge key={tag} variant="secondary">
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Reviews */}
            <Card>
                <CardHeader>
                    <CardTitle>Reviews ({reviews.length})</CardTitle>
                    <CardDescription>
                        Feedback and suggestions from reviewers
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {reviews.length === 0 ? (
                        <div className="text-center py-8">
                            <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No reviews yet</h3>
                            <p className="text-muted-foreground">
                                This document hasn't been reviewed yet. Reviews will appear here once they are submitted.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {reviews.map((review) => (
                                <div key={review.id} className="border border-border rounded-lg p-4 bg-background">
                                    <div className="flex items-start justify-between mb-3">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="font-medium">{review.reviewer}</span>
                                                {review.rating && (
                                                    <span className="text-sm text-warning">
                                                        {getRatingStars(review.rating)}
                                                    </span>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                <Calendar className="h-4 w-4" />
                                                {formatDate(review.reviewedAt)}
                                            </div>
                                        </div>
                                        <Badge variant={review.status === 'completed' ? 'default' : 'secondary'} className={review.status === 'completed' ? 'bg-success/10 text-success-foreground' : 'bg-muted text-muted-foreground'}>
                                            {review.status}
                                        </Badge>
                                    </div>

                                    <p className="text-sm mb-3">{review.comments}</p>

                                    {review.suggestions.length > 0 && (
                                        <div>
                                            <h5 className="font-medium mb-2">Suggestions:</h5>
                                            <ul className="text-sm space-y-1">
                                                {review.suggestions.map((suggestion, index) => (
                                                    <li key={index} className="flex items-start gap-2">
                                                        <span className="text-muted-foreground">•</span>
                                                        <span>{suggestion}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Citations */}
            <CitationsSection documentId={upload.id} />

            {/* Actions */}
            <Card>
                <CardHeader>
                    <CardTitle>Actions</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center gap-4">
                        <Button variant="outline" asChild>
                            <Link to={`/reviews/${upload.id}/new`}>
                                <span className="flex items-center">
                                    <MessageSquare className="h-4 w-4 mr-2" />
                                    <span>Add Review</span>
                                </span>
                            </Link>
                        </Button>
                        <Button variant="outline">
                            <Share2 className="h-4 w-4 mr-2" />
                            Share Document
                        </Button>
                        <Button variant="outline">
                            <Download className="h-4 w-4 mr-2" />
                            Download
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default UploadDetailPage;
