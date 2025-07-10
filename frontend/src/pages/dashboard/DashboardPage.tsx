import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, Eye, Clock, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const DashboardPage: React.FC = () => {
    // TODO: Replace with actual data from API
    const stats = {
        totalUploads: 24,
        pendingReviews: 8,
        completedReviews: 16,
        recentActivity: 3
    };

    const recentUploads = [
        { id: '1', name: 'Project Architecture.pdf', status: 'pending', uploadedAt: '2 hours ago' },
        { id: '2', name: 'API Documentation.md', status: 'reviewed', uploadedAt: '1 day ago' },
        { id: '3', name: 'Database Schema.sql', status: 'in-review', uploadedAt: '2 days ago' }
    ];

    const recentReviews = [
        { id: '1', fileName: 'Security Guidelines.pdf', reviewer: 'John Doe', status: 'completed', reviewedAt: '1 hour ago' },
        { id: '2', fileName: 'Code Standards.md', reviewer: 'Jane Smith', status: 'in-progress', reviewedAt: '3 hours ago' }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-accent/10">
            <div className="container mx-auto px-6 py-8 space-y-8">
                {/* Header Section */}
                <div className="text-center space-y-4">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
                        Dashboard
                    </h1>
                    <p className="text-body-lg text-muted-foreground max-w-2xl mx-auto">
                        Welcome back! Here's an overview of your document review activity.
                    </p>
                </div>

            {/* Stats Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="hover-lift glass-card">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Uploads</CardTitle>
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Upload className="h-4 w-4 text-primary" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-primary">{stats.totalUploads}</div>
                        <p className="text-xs text-muted-foreground flex items-center mt-1">
                            <span className="text-green-600 mr-1">+3</span> from last week
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover-lift glass-card">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
                        <div className="p-2 bg-amber-500/10 rounded-lg">
                            <Clock className="h-4 w-4 text-amber-600" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-amber-600">{stats.pendingReviews}</div>
                        <p className="text-xs text-muted-foreground flex items-center mt-1">
                            <span className="text-green-600 mr-1">-2</span> from yesterday
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover-lift glass-card">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Completed Reviews</CardTitle>
                        <div className="p-2 bg-green-500/10 rounded-lg">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-600">{stats.completedReviews}</div>
                        <p className="text-xs text-muted-foreground flex items-center mt-1">
                            <span className="text-green-600 mr-1">+5</span> from last week
                        </p>
                    </CardContent>
                </Card>

                <Card className="hover-lift glass-card">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Eye className="h-4 w-4 text-primary" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-primary">{stats.recentActivity}</div>
                        <p className="text-xs text-muted-foreground">in the last hour</p>
                    </CardContent>
                </Card>
            </div>

            {/* Quick Actions */}
            <Card className="glass-card">
                <CardHeader>
                    <CardTitle className="text-xl font-semibold">Quick Actions</CardTitle>
                    <CardDescription>Get started with common tasks</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col sm:flex-row gap-4">
                    <Button asChild size="lg" className="group hover-lift">
                        <Link to="/uploads/new">
                            <Upload className="mr-2 h-5 w-5 transition-transform group-hover:scale-110" />
                            Upload Document
                        </Link>
                    </Button>
                    <Button variant="outline" asChild size="lg" className="hover-lift">
                        <Link to="/uploads">
                            <FileText className="mr-2 h-5 w-5" />
                            View All Uploads
                        </Link>
                    </Button>
                    <Button variant="outline" asChild size="lg" className="hover-lift">
                        <Link to="/reviews">
                            <Eye className="mr-2 h-5 w-5" />
                            Review Documents
                        </Link>
                    </Button>
                </CardContent>
            </Card>

            {/* Recent Activity */}
            <div className="grid gap-6 md:grid-cols-2">
                <Card className="glass-card">
                    <CardHeader>
                        <CardTitle className="text-xl font-semibold">Recent Uploads</CardTitle>
                        <CardDescription>Your latest document uploads</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {recentUploads.map((upload) => (
                                <div key={upload.id} className="flex items-center justify-between p-4 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors border border-border/50">
                                    <div>
                                        <Link
                                            to={`/uploads/${upload.id}`}
                                            className="font-medium hover:text-primary transition-colors"
                                        >
                                            {upload.name}
                                        </Link>
                                        <p className="text-xs text-muted-foreground">{upload.uploadedAt}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Badge 
                                            variant={upload.status === 'pending' ? 'secondary' : 
                                                   upload.status === 'reviewed' ? 'default' : 'outline'}
                                            className="capitalize"
                                        >
                                            {upload.status}
                                        </Badge>
                                        <Button variant="ghost" size="sm" asChild>
                                            <Link to={`/uploads/${upload.id}`}>
                                                <Eye className="h-4 w-4" />
                                            </Link>
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="mt-6">
                            <Button variant="ghost" size="sm" asChild className="w-full hover-lift">
                                <Link to="/uploads">View all uploads →</Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card">
                    <CardHeader>
                        <CardTitle className="text-xl font-semibold">Recent Reviews</CardTitle>
                        <CardDescription>Latest review activity</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {recentReviews.map((review) => (
                                <div key={review.id} className="p-4 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors border border-border/50">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <Link
                                                to={`/reviews/${review.id}`}
                                                className="font-medium hover:text-primary transition-colors"
                                            >
                                                {review.fileName}
                                            </Link>
                                            <p className="text-sm text-muted-foreground">by {review.reviewer}</p>
                                            <p className="text-xs text-muted-foreground">{review.reviewedAt}</p>
                                        </div>
                                        <Badge 
                                            variant={review.status === 'completed' ? 'default' : 'secondary'}
                                            className="capitalize"
                                        >
                                            {review.status}
                                        </Badge>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="mt-6">
                            <Button variant="ghost" size="sm" asChild className="w-full hover-lift">
                                <Link to="/reviews">View all reviews →</Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    </div>
    );
};

export default DashboardPage;
