import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground">
                    Welcome back! Here's an overview of your document review activity.
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Uploads</CardTitle>
                        <Upload className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.totalUploads}</div>
                        <p className="text-xs text-muted-foreground">+3 from last week</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
                        <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.pendingReviews}</div>
                        <p className="text-xs text-muted-foreground">-2 from yesterday</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Completed Reviews</CardTitle>
                        <CheckCircle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.completedReviews}</div>
                        <p className="text-xs text-muted-foreground">+5 from last week</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
                        <Eye className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.recentActivity}</div>
                        <p className="text-xs text-muted-foreground">in the last hour</p>
                    </CardContent>
                </Card>
            </div>

            {/* Quick Actions */}
            <Card>
                <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                    <CardDescription>Get started with common tasks</CardDescription>
                </CardHeader>
                <CardContent className="flex gap-4">
                    <Button asChild>
                        <Link to="/uploads/new">
                            <Upload className="mr-2 h-4 w-4" />
                            Upload Document
                        </Link>
                    </Button>
                    <Button variant="outline" asChild>
                        <Link to="/uploads">
                            <FileText className="mr-2 h-4 w-4" />
                            View All Uploads
                        </Link>
                    </Button>
                    <Button variant="outline" asChild>
                        <Link to="/reviews">
                            <Eye className="mr-2 h-4 w-4" />
                            Review Documents
                        </Link>
                    </Button>
                </CardContent>
            </Card>

            {/* Recent Activity */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Uploads</CardTitle>
                        <CardDescription>Your latest document uploads</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {recentUploads.map((upload) => (
                                <div key={upload.id} className="flex items-center justify-between border-b pb-2 last:border-b-0">
                                    <div>
                                        <Link
                                            to={`/uploads/${upload.id}`}
                                            className="font-medium hover:underline"
                                        >
                                            {upload.name}
                                        </Link>
                                        <p className="text-xs text-muted-foreground">{upload.uploadedAt}</p>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded ${upload.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                            upload.status === 'reviewed' ? 'bg-green-100 text-green-800' :
                                                'bg-blue-100 text-blue-800'
                                        }`}>
                                        {upload.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div className="mt-4">
                            <Button variant="ghost" size="sm" asChild>
                                <Link to="/uploads">View all uploads →</Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Recent Reviews</CardTitle>
                        <CardDescription>Latest review activity</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {recentReviews.map((review) => (
                                <div key={review.id} className="flex items-center justify-between border-b pb-2 last:border-b-0">
                                    <div>
                                        <Link
                                            to={`/reviews/${review.id}`}
                                            className="font-medium hover:underline"
                                        >
                                            {review.fileName}
                                        </Link>
                                        <p className="text-xs text-muted-foreground">by {review.reviewer} • {review.reviewedAt}</p>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded ${review.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            'bg-blue-100 text-blue-800'
                                        }`}>
                                        {review.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div className="mt-4">
                            <Button variant="ghost" size="sm" asChild>
                                <Link to="/reviews">View all reviews →</Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default DashboardPage;
