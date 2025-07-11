import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
    AlertTriangle
} from 'lucide-react';

const ReviewDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);

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

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'pending': return 'bg-yellow-100 text-yellow-800';
            case 'in-progress': return 'bg-blue-100 text-blue-800';
            case 'completed': return 'bg-green-100 text-green-800';
            case 'rejected': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'pending': return <Clock className="h-4 w-4" />;
            case 'in-progress': return <Eye className="h-4 w-4" />;
            case 'completed': return <CheckCircle className="h-4 w-4" />;
            case 'rejected': return <XCircle className="h-4 w-4" />;
            default: return <FileText className="h-4 w-4" />;
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'bg-red-100 text-red-800';
            case 'medium': return 'bg-yellow-100 text-yellow-800';
            case 'low': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
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

    const renderStarRating = () => {
        return (
            <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Rating:</span>
                <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }, (_, i) => (
                        <button
                            key={i}
                            type="button"
                            onClick={() => handleRatingClick(i + 1)}
                            className="focus:outline-none"
                        >
                            <Star
                                className={`h-6 w-6 cursor-pointer transition-colors ${i < reviewData.rating
                                        ? 'text-yellow-400 fill-yellow-400'
                                        : 'text-gray-300 hover:text-yellow-300'
                                    }`}
                            />
                        </button>
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
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back to Reviews
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
                                <Badge className={getStatusColor(review.status)}>
                                    {getStatusIcon(review.status)}
                                    <span className="ml-1 capitalize">{review.status}</span>
                                </Badge>
                                <Badge className={getPriorityColor(review.priority)}>
                                    {review.priority} priority
                                </Badge>
                                {review.dueDate && isOverdue(review.dueDate) && review.status !== 'completed' && (
                                    <Badge className="bg-red-100 text-red-800">
                                        <AlertTriangle className="h-4 w-4 mr-1" />
                                        Overdue
                                    </Badge>
                                )}
                            </div>
                            <CardDescription className="text-base">
                                {review.documentDescription}
                            </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" asChild>
                                <Link to={`/uploads/${review.documentId}`}>
                                    <Eye className="h-4 w-4 mr-2" />
                                    View Document
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
                                    <span className={`font-medium ${isOverdue(review.dueDate) ? 'text-red-600' : ''}`}>
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
                                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                                <span className="text-sm">{guideline}</span>
                            </li>
                        ))}
                    </ul>
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
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                        <div className="flex items-center gap-4 pt-4 border-t">
                            <Button
                                onClick={() => handleSubmit('approve')}
                                disabled={isSubmitting || !reviewData.comments.trim() || reviewData.rating === 0}
                                className="bg-green-600 hover:bg-green-700"
                            >
                                <ThumbsUp className="h-4 w-4 mr-2" />
                                {isSubmitting ? 'Submitting...' : 'Approve'}
                            </Button>

                            <Button
                                onClick={() => handleSubmit('request-changes')}
                                disabled={isSubmitting || !reviewData.comments.trim() || reviewData.rating === 0}
                                variant="outline"
                                className="border-yellow-500 text-yellow-700 hover:bg-yellow-50"
                            >
                                <AlertTriangle className="h-4 w-4 mr-2" />
                                {isSubmitting ? 'Submitting...' : 'Request Changes'}
                            </Button>

                            <Button
                                onClick={() => handleSubmit('reject')}
                                disabled={isSubmitting || !reviewData.comments.trim() || reviewData.rating === 0}
                                variant="outline"
                                className="border-red-500 text-red-700 hover:bg-red-50"
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
                            <CheckCircle className="h-12 w-12 mx-auto text-green-600 mb-4" />
                            <h3 className="text-lg font-semibold mb-2">Review Submitted Successfully</h3>
                            <p className="text-muted-foreground">
                                Your review has been submitted and the document author has been notified.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default ReviewDetailPage;
