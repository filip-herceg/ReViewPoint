/**
 * User Management Page
 * 
 * Administrative interface for managing user accounts, roles, and permissions.
 * Only accessible to users with 'admin' role.
 */

import React from 'react';
import { RequireRole } from '@/components/auth/AuthGuard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Users, UserPlus, Shield, Edit, Trash2 } from 'lucide-react';

// Mock user data for demonstration
const mockUsers = [
    {
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
        roles: ['admin'],
        status: 'active',
        lastActive: '2025-01-09',
    },
    {
        id: 2,
        name: 'Jane Smith',
        email: 'jane@example.com',
        roles: ['moderator'],
        status: 'active',
        lastActive: '2025-01-08',
    },
    {
        id: 3,
        name: 'Bob Wilson',
        email: 'bob@example.com',
        roles: ['user'],
        status: 'active',
        lastActive: '2025-01-07',
    },
    {
        id: 4,
        name: 'Alice Johnson',
        email: 'alice@example.com',
        roles: ['user'],
        status: 'inactive',
        lastActive: '2024-12-15',
    },
];

export default function UserManagementPage() {
    return (
        <RequireRole
            role="admin"
            fallback={
                <Alert variant="destructive">
                    <Shield className="h-4 w-4" />
                    <AlertDescription>
                        You need administrator privileges to access user management.
                    </AlertDescription>
                </Alert>
            }
        >
            <div className="space-y-6">
                {/* Page Header */}
                <div className="flex items-center justify-between border-b border-gray-200 pb-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                            <Users className="h-8 w-8" />
                            User Management
                        </h1>
                        <p className="text-gray-600 mt-2">
                            Manage user accounts, roles, and permissions
                        </p>
                    </div>
                    <Button className="flex items-center gap-2">
                        <UserPlus className="h-4 w-4" />
                        Add New User
                    </Button>
                </div>

                {/* User Statistics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-blue-600">
                                {mockUsers.length}
                            </div>
                            <div className="text-sm text-gray-600">Total Users</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-green-600">
                                {mockUsers.filter(u => u.status === 'active').length}
                            </div>
                            <div className="text-sm text-gray-600">Active Users</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-purple-600">
                                {mockUsers.filter(u => u.roles.includes('admin')).length}
                            </div>
                            <div className="text-sm text-gray-600">Administrators</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-orange-600">
                                {mockUsers.filter(u => u.roles.includes('moderator')).length}
                            </div>
                            <div className="text-sm text-gray-600">Moderators</div>
                        </CardContent>
                    </Card>
                </div>

                {/* Users Table */}
                <Card>
                    <CardHeader>
                        <CardTitle>All Users</CardTitle>
                        <CardDescription>
                            Manage user accounts and permissions
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            User
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Email
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Roles
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Last Active
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {mockUsers.map((user) => (
                                        <tr key={user.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {user.name}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {user.email}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex gap-1">
                                                    {user.roles.map((role) => (
                                                        <Badge
                                                            key={role}
                                                            variant={
                                                                role === 'admin'
                                                                    ? 'destructive'
                                                                    : role === 'moderator'
                                                                        ? 'default'
                                                                        : 'secondary'
                                                            }
                                                        >
                                                            {role}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <Badge
                                                    variant={
                                                        user.status === 'active'
                                                            ? 'default'
                                                            : 'secondary'
                                                    }
                                                >
                                                    {user.status}
                                                </Badge>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {user.lastActive}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex gap-2">
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        className="h-8 w-8 p-0"
                                                    >
                                                        <Edit className="h-4 w-4" />
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </RequireRole>
    );
}
