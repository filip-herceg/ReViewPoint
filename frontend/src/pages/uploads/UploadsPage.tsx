import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    Upload,
    FileText,
    Filter,
    Search,
    Calendar,
    User,
    Clock,
    CheckCircle,
    XCircle,
    Eye
} from 'lucide-react';
import { Link } from 'react-router-dom';

const UploadsPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');

    // TODO: Replace with actual data from API
    const uploads = [
        {
            id: '1',
            name: 'Project Architecture.pdf',
            description: 'System architecture documentation for the new platform',
            status: 'pending',
            uploadedAt: '2024-01-15T10:30:00Z',
            uploadedBy: 'John Doe',
            fileSize: '2.4 MB',
            fileType: 'pdf',
            reviewCount: 0,
            tags: ['architecture', 'documentation']
        },
        {
            id: '2',
            name: 'API Documentation.md',
            description: 'REST API endpoints and usage guidelines',
            status: 'reviewed',
            uploadedAt: '2024-01-14T14:20:00Z',
            uploadedBy: 'Jane Smith',
            fileSize: '1.2 MB',
            fileType: 'markdown',
            reviewCount: 2,
            tags: ['api', 'documentation']
        },
        {
            id: '3',
            name: 'Database Schema.sql',
            description: 'Database schema and migration scripts',
            status: 'in-review',
            uploadedAt: '2024-01-13T09:15:00Z',
            uploadedBy: 'Bob Johnson',
            fileSize: '856 KB',
            fileType: 'sql',
            reviewCount: 1,
            tags: ['database', 'schema']
        },
        {
            id: '4',
            name: 'Security Guidelines.pdf',
            description: 'Security best practices and guidelines',
            status: 'rejected',
            uploadedAt: '2024-01-12T16:45:00Z',
            uploadedBy: 'Alice Wilson',
            fileSize: '3.1 MB',
            fileType: 'pdf',
            reviewCount: 3,
            tags: ['security', 'guidelines']
        }
    ];

    const filteredUploads = uploads.filter(upload => {
        const matchesSearch = upload.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            upload.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || upload.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'pending': return 'bg-yellow-100 text-yellow-800';
            case 'in-review': return 'bg-blue-100 text-blue-800';
            case 'reviewed': return 'bg-green-100 text-green-800';
            case 'rejected': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'pending': return <Clock className="h-4 w-4" />;
            case 'in-review': return <Eye className="h-4 w-4" />;
            case 'reviewed': return <CheckCircle className="h-4 w-4" />;
            case 'rejected': return <XCircle className="h-4 w-4" />;
            default: return <FileText className="h-4 w-4" />;
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Uploads</h1>
                    <p className="text-muted-foreground">
                        Manage your document uploads and track their review status.
                    </p>
                </div>
                <Button asChild>
                    <Link to="/uploads/new">
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Document
                    </Link>
                </Button>
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
                                placeholder="Search uploads..."
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
                                <option value="in-review">In Review</option>
                                <option value="reviewed">Reviewed</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Upload Statistics */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Total Uploads</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{uploads.length}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Pending</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-yellow-600">
                            {uploads.filter(u => u.status === 'pending').length}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">In Review</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">
                            {uploads.filter(u => u.status === 'in-review').length}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Reviewed</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">
                            {uploads.filter(u => u.status === 'reviewed').length}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Uploads List */}
            <div className="space-y-4">
                {filteredUploads.map((upload) => (
                    <Card key={upload.id}>
                        <CardContent className="pt-6">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <Link
                                            to={`/uploads/${upload.id}`}
                                            className="text-lg font-semibold hover:underline"
                                        >
                                            {upload.name}
                                        </Link>
                                        <Badge className={getStatusColor(upload.status)}>
                                            {getStatusIcon(upload.status)}
                                            <span className="ml-1 capitalize">{upload.status}</span>
                                        </Badge>
                                    </div>

                                    <p className="text-muted-foreground mb-3">{upload.description}</p>

                                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                        <div className="flex items-center gap-1">
                                            <User className="h-4 w-4" />
                                            {upload.uploadedBy}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Calendar className="h-4 w-4" />
                                            {formatDate(upload.uploadedAt)}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <FileText className="h-4 w-4" />
                                            {upload.fileSize}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Eye className="h-4 w-4" />
                                            {upload.reviewCount} reviews
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 mt-3">
                                        {upload.tags.map((tag) => (
                                            <Badge key={tag} variant="secondary" className="text-xs">
                                                {tag}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Button variant="outline" size="sm" asChild>
                                        <Link to={`/uploads/${upload.id}`}>View Details</Link>
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {filteredUploads.length === 0 && (
                    <Card>
                        <CardContent className="pt-6 text-center">
                            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No uploads found</h3>
                            <p className="text-muted-foreground mb-4">
                                {searchTerm || statusFilter !== 'all'
                                    ? 'Try adjusting your search or filter criteria.'
                                    : 'Get started by uploading your first document.'
                                }
                            </p>
                            {!searchTerm && statusFilter === 'all' && (
                                <Button asChild>
                                    <Link to="/uploads/new">
                                        <Upload className="mr-2 h-4 w-4" />
                                        Upload Document
                                    </Link>
                                </Button>
                            )}
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
};

export default UploadsPage;
