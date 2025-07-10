import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
    Eye,
    FileText,
    Filter,
    Search,
    Calendar,
    User,
    Clock,
    CheckCircle,
    XCircle,
    Star,
    MessageSquare
} from 'lucide-react';
import { Link } from 'react-router-dom';

const ReviewsPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [viewMode, setViewMode] = useState<'assigned' | 'completed' | 'all'>('all');

    // TODO: Replace with actual data from API
    const reviews = [
        {
            id: '1',
            documentId: '1',
            documentName: 'Project Architecture.pdf',
            documentDescription: 'System architecture documentation for the new platform',
            status: 'pending',
            assignedTo: 'Current User',
            assignedAt: '2024-01-16T08:30:00Z',
            dueDate: '2024-01-20T23:59:59Z',
            priority: 'high',
            author: 'John Doe',
            tags: ['architecture', 'documentation']
        },
        {
            id: '2',
            documentId: '2',
            documentName: 'API Documentation.md',
            documentDescription: 'REST API endpoints and usage guidelines',
            status: 'completed',
            assignedTo: 'Current User',
            assignedAt: '2024-01-14T10:00:00Z',
            completedAt: '2024-01-15T16:45:00Z',
            rating: 4,
            priority: 'medium',
            author: 'Jane Smith',
            tags: ['api', 'documentation']
        },
        {
            id: '3',
            documentId: '3',
            documentName: 'Database Schema.sql',
            documentDescription: 'Database schema and migration scripts',
            status: 'in-progress',
            assignedTo: 'Current User',
            assignedAt: '2024-01-13T14:20:00Z',
            dueDate: '2024-01-18T23:59:59Z',
            priority: 'low',
            author: 'Bob Johnson',
            tags: ['database', 'schema']
        },
        {
            id: '4',
            documentId: '4',
            documentName: 'Security Guidelines.pdf',
            documentDescription: 'Security best practices and guidelines',
            status: 'rejected',
            assignedTo: 'Alice Wilson',
            assignedAt: '2024-01-12T09:00:00Z',
            completedAt: '2024-01-13T11:30:00Z',
            rating: 2,
            priority: 'high',
            author: 'Charlie Brown',
            tags: ['security', 'guidelines']
        }
    ];

    const filteredReviews = reviews.filter(review => {
        const matchesSearch = review.documentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            review.documentDescription.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || review.status === statusFilter;
        const matchesView = viewMode === 'all' ||
            (viewMode === 'assigned' && review.assignedTo === 'Current User' && review.status !== 'completed') ||
            (viewMode === 'completed' && review.status === 'completed');
        return matchesSearch && matchesStatus && matchesView;
    });

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300';
            case 'in-progress': return 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary-foreground';
            case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300';
            case 'rejected': return 'bg-destructive/10 text-destructive dark:bg-destructive/20 dark:text-destructive-foreground';
            default: return 'bg-muted text-muted-foreground';
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
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const isOverdue = (dueDateString: string) => {
        return new Date(dueDateString) < new Date();
    };

    const getRatingStars = (rating: number) => {
        return Array.from({ length: 5 }, (_, i) => (
            <Star
                key={i}
                className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
            />
        ));
    };

    const getStats = () => {
        const myReviews = reviews.filter(r => r.assignedTo === 'Current User');
        return {
            total: reviews.length,
            assigned: myReviews.filter(r => r.status !== 'completed').length,
            completed: myReviews.filter(r => r.status === 'completed').length,
            overdue: myReviews.filter(r => r.dueDate && isOverdue(r.dueDate) && r.status !== 'completed').length
        };
    };

    const stats = getStats();

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Reviews</h1>
                <p className="text-muted-foreground">
                    Review documents assigned to you and track your review history.
                </p>
            </div>

            {/* View Mode Tabs */}
            <div className="flex items-center gap-2">
                <Button
                    variant={viewMode === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('all')}
                >
                    All Reviews
                </Button>
                <Button
                    variant={viewMode === 'assigned' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('assigned')}
                >
                    Assigned to Me ({stats.assigned})
                </Button>
                <Button
                    variant={viewMode === 'completed' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('completed')}
                >
                    Completed ({stats.completed})
                </Button>
            </div>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Total Reviews</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Assigned to Me</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">{stats.assigned}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Completed</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Overdue</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Search and Filter */}
            <Card>
                <CardHeader>
                    <CardTitle>Search and Filter</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-4">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search reviews..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <Filter className="h-4 w-4 text-muted-foreground" />
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="px-3 py-2 border rounded-md"
                            >
                                <option value="all">All Status</option>
                                <option value="pending">Pending</option>
                                <option value="in-progress">In Progress</option>
                                <option value="completed">Completed</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Reviews List */}
            <div className="space-y-4">
                {filteredReviews.map((review) => (
                    <Card key={review.id}>
                        <CardContent className="pt-6">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <Link
                                            to={`/reviews/${review.id}`}
                                            className="text-lg font-semibold hover:underline"
                                        >
                                            {review.documentName}
                                        </Link>
                                        <Badge className={getStatusColor(review.status)}>
                                            {getStatusIcon(review.status)}
                                            <span className="ml-1 capitalize">{review.status}</span>
                                        </Badge>
                                        <Badge className={getPriorityColor(review.priority)}>
                                            {review.priority} priority
                                        </Badge>
                                        {review.dueDate && isOverdue(review.dueDate) && review.status !== 'completed' && (
                                            <Badge className="bg-red-100 text-red-800">
                                                Overdue
                                            </Badge>
                                        )}
                                    </div>

                                    <p className="text-muted-foreground mb-3">{review.documentDescription}</p>

                                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                        <div className="flex items-center gap-1">
                                            <User className="h-4 w-4" />
                                            Author: {review.author}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Calendar className="h-4 w-4" />
                                            Assigned: {formatDate(review.assignedAt)}
                                        </div>
                                        {review.dueDate && (
                                            <div className="flex items-center gap-1">
                                                <Clock className="h-4 w-4" />
                                                Due: {formatDate(review.dueDate)}
                                            </div>
                                        )}
                                        {review.completedAt && (
                                            <div className="flex items-center gap-1">
                                                <CheckCircle className="h-4 w-4" />
                                                Completed: {formatDate(review.completedAt)}
                                            </div>
                                        )}
                                    </div>

                                    {review.rating && (
                                        <div className="flex items-center gap-2 mt-3">
                                            <span className="text-sm text-muted-foreground">Rating:</span>
                                            <div className="flex items-center gap-1">
                                                {getRatingStars(review.rating)}
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex items-center gap-2 mt-3">
                                        {review.tags.map((tag) => (
                                            <Badge key={tag} variant="secondary" className="text-xs">
                                                {tag}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    {review.status === 'pending' || review.status === 'in-progress' ? (
                                        <Button size="sm" asChild>
                                            <Link to={`/reviews/${review.id}`}>
                                                <Eye className="h-4 w-4 mr-2" />
                                                Review
                                            </Link>
                                        </Button>
                                    ) : (
                                        <Button variant="outline" size="sm" asChild>
                                            <Link to={`/reviews/${review.id}`}>
                                                <MessageSquare className="h-4 w-4 mr-2" />
                                                View Details
                                            </Link>
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {filteredReviews.length === 0 && (
                    <Card>
                        <CardContent className="pt-6 text-center">
                            <Eye className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No reviews found</h3>
                            <p className="text-muted-foreground">
                                {searchTerm || statusFilter !== 'all'
                                    ? 'Try adjusting your search or filter criteria.'
                                    : viewMode === 'assigned'
                                        ? 'You have no pending reviews assigned to you.'
                                        : 'No reviews are available at the moment.'
                                }
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
};

export default ReviewsPage;
