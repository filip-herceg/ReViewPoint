/**
 * Admin Panel Page
 * 
 * Main administrative dashboard with overview of system statistics
 * and quick access to admin tools. Only accessible to users with 'admin' role.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { RequireRole, ShowForRole } from '@/components/auth/AuthGuard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Users, Settings, BarChart3, Shield, AlertCircle } from 'lucide-react';

export default function AdminPanelPage() {
    return (
        <RequireRole
            role="admin"
            fallback={
                <Alert variant="destructive">
                    <Shield className="h-4 w-4" />
                    <AlertDescription>
                        You need administrator privileges to access this page.
                    </AlertDescription>
                </Alert>
            }
        >
            <div className="space-y-6">
                {/* Page Header */}
                <div className="border-b border-gray-200 pb-4">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
                    <p className="text-gray-600 mt-2">
                        System administration and management tools
                    </p>
                </div>

                {/* Admin Tools Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* User Management */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Users className="h-5 w-5" />
                                User Management
                            </CardTitle>
                            <CardDescription>
                                Manage user accounts, roles, and permissions
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                <div className="text-sm text-gray-600">
                                    • View and edit user profiles
                                </div>
                                <div className="text-sm text-gray-600">
                                    • Assign roles and permissions
                                </div>
                                <div className="text-sm text-gray-600">
                                    • Deactivate accounts
                                </div>
                                <Button asChild className="w-full mt-4">
                                    <Link to="/admin/users">Manage Users</Link>
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* System Settings */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Settings className="h-5 w-5" />
                                System Settings
                            </CardTitle>
                            <CardDescription>
                                Configure system-wide settings and preferences
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                <div className="text-sm text-gray-600">
                                    • Upload limits and restrictions
                                </div>
                                <div className="text-sm text-gray-600">
                                    • Email and notification settings
                                </div>
                                <div className="text-sm text-gray-600">
                                    • Security configuration
                                </div>
                                <Button asChild className="w-full mt-4">
                                    <Link to="/admin/settings">System Settings</Link>
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Analytics */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <BarChart3 className="h-5 w-5" />
                                Analytics & Reports
                            </CardTitle>
                            <CardDescription>
                                View system usage statistics and reports
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                <div className="text-sm text-gray-600">
                                    • User activity reports
                                </div>
                                <div className="text-sm text-gray-600">
                                    • Upload and review statistics
                                </div>
                                <div className="text-sm text-gray-600">
                                    • System performance metrics
                                </div>
                                <Button asChild className="w-full mt-4" variant="outline">
                                    <Link to="/admin/analytics">View Analytics</Link>
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-blue-600">1,234</div>
                            <div className="text-sm text-gray-600">Total Users</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-green-600">456</div>
                            <div className="text-sm text-gray-600">Active Sessions</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-purple-600">789</div>
                            <div className="text-sm text-gray-600">Total Uploads</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-orange-600">12</div>
                            <div className="text-sm text-gray-600">Pending Reviews</div>
                        </CardContent>
                    </Card>
                </div>

                {/* Admin-only Features Demo */}
                <ShowForRole role="admin">
                    <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                            This alert is only visible to administrators using the ShowForRole component.
                        </AlertDescription>
                    </Alert>
                </ShowForRole>
            </div>
        </RequireRole>
    );
}
