import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Bell,
    Shield,
    Palette,
    Globe,
    Save,
    Moon,
    Sun,
    Monitor,
    Mail,
    MessageSquare,
    AlertCircle,
    Eye,
    EyeOff
} from 'lucide-react';
import { useAuthStore } from '@/lib/store/authStore';

const SettingsPage: React.FC = () => {
    const { user } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('notifications');

    // Settings state
    const [settings, setSettings] = useState({
        notifications: {
            email: true,
            push: true,
            reviewRequests: true,
            documentUploads: true,
            systemUpdates: false
        },
        privacy: {
            profileVisibility: 'public' as 'public' | 'private',
            showEmail: false,
            showActivity: true
        },
        appearance: {
            theme: 'system' as 'light' | 'dark' | 'system',
            language: 'en'
        },
        security: {
            twoFactorEnabled: false,
            sessionTimeout: '30'
        }
    });

    const handleSave = async () => {
        setIsLoading(true);
        try {
            // TODO: Replace with actual API call
            await new Promise(resolve => setTimeout(resolve, 1000));

            console.log('Saving settings:', settings);
            alert('Settings saved successfully!');
        } catch (error) {
            console.error('Failed to save settings:', error);
            alert('Failed to save settings. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const updateNotificationSetting = (key: string, value: boolean) => {
        setSettings(prev => ({
            ...prev,
            notifications: {
                ...prev.notifications,
                [key]: value
            }
        }));
    };

    const updatePrivacySetting = (key: string, value: any) => {
        setSettings(prev => ({
            ...prev,
            privacy: {
                ...prev.privacy,
                [key]: value
            }
        }));
    };

    const updateAppearanceSetting = (key: string, value: any) => {
        setSettings(prev => ({
            ...prev,
            appearance: {
                ...prev.appearance,
                [key]: value
            }
        }));
    };

    const updateSecuritySetting = (key: string, value: any) => {
        setSettings(prev => ({
            ...prev,
            security: {
                ...prev.security,
                [key]: value
            }
        }));
    };

    const tabs = [
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'privacy', label: 'Privacy', icon: Eye },
        { id: 'appearance', label: 'Appearance', icon: Palette },
        { id: 'security', label: 'Security', icon: Shield }
    ];

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="text-muted-foreground">
                    Manage your account preferences and application settings.
                </p>
            </div>

            <div className="flex flex-col lg:flex-row gap-6">
                {/* Sidebar */}
                <div className="lg:w-64">
                    <Card>
                        <CardContent className="p-4">
                            <nav className="space-y-2">
                                {tabs.map((tab) => {
                                    const Icon = tab.icon;
                                    return (
                                        <button
                                            key={tab.id}
                                            onClick={() => setActiveTab(tab.id)}
                                            className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-md transition-colors ${activeTab === tab.id
                                                ? 'bg-primary/10 text-primary'
                                                : 'hover:bg-muted'
                                                }`}
                                        >
                                            <Icon className="w-4 h-4" />
                                            <span className="text-sm font-medium">{tab.label}</span>
                                        </button>
                                    );
                                })}
                            </nav>
                        </CardContent>
                    </Card>
                </div>

                {/* Content */}
                <div className="flex-1">
                    {activeTab === 'notifications' && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Bell className="w-5 h-5" />
                                    Notification Settings
                                </CardTitle>
                                <CardDescription>
                                    Choose what notifications you want to receive
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Email Notifications</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Receive notifications via email
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.notifications.email}
                                            onChange={(e) => updateNotificationSetting('email', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Push Notifications</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Receive push notifications in your browser
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.notifications.push}
                                            onChange={(e) => updateNotificationSetting('push', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Review Requests</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Get notified when you're assigned to review a document
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.notifications.reviewRequests}
                                            onChange={(e) => updateNotificationSetting('reviewRequests', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Document Uploads</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Get notified when new documents are uploaded
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.notifications.documentUploads}
                                            onChange={(e) => updateNotificationSetting('documentUploads', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">System Updates</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Get notified about system maintenance and updates
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.notifications.systemUpdates}
                                            onChange={(e) => updateNotificationSetting('systemUpdates', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {activeTab === 'privacy' && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Eye className="w-5 h-5" />
                                    Privacy Settings
                                </CardTitle>
                                <CardDescription>
                                    Control your privacy and data sharing preferences
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-4">
                                    <div>
                                        <h4 className="font-medium mb-2">Profile Visibility</h4>
                                        <div className="space-y-2">
                                            <label className="flex items-center gap-2">
                                                <input
                                                    type="radio"
                                                    name="profileVisibility"
                                                    value="public"
                                                    checked={settings.privacy.profileVisibility === 'public'}
                                                    onChange={(e) => updatePrivacySetting('profileVisibility', e.target.value)}
                                                    className="h-4 w-4 text-primary focus:ring-primary border-border"
                                                />
                                                <span className="text-sm">Public - Anyone can see your profile</span>
                                            </label>
                                            <label className="flex items-center gap-2">
                                                <input
                                                    type="radio"
                                                    name="profileVisibility"
                                                    value="private"
                                                    checked={settings.privacy.profileVisibility === 'private'}
                                                    onChange={(e) => updatePrivacySetting('profileVisibility', e.target.value)}
                                                    className="h-4 w-4 text-primary focus:ring-primary border-border"
                                                />
                                                <span className="text-sm">Private - Only you can see your profile</span>
                                            </label>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Show Email Address</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Display your email address on your public profile
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.privacy.showEmail}
                                            onChange={(e) => updatePrivacySetting('showEmail', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Show Activity</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Display your recent activity and statistics
                                            </p>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={settings.privacy.showActivity}
                                            onChange={(e) => updatePrivacySetting('showActivity', e.target.checked)}
                                            className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
                                        />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {activeTab === 'appearance' && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Palette className="w-5 h-5" />
                                    Appearance Settings
                                </CardTitle>
                                <CardDescription>
                                    Customize the look and feel of the application
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div>
                                    <h4 className="font-medium mb-3">Theme</h4>
                                    <div className="grid grid-cols-3 gap-3">
                                        <button
                                            onClick={() => updateAppearanceSetting('theme', 'light')}
                                            className={`p-3 border rounded-lg flex flex-col items-center gap-2 transition-colors ${settings.appearance.theme === 'light'
                                                ? 'border-primary bg-primary/10'
                                                : 'border-border hover:bg-muted'
                                                }`}
                                        >
                                            <Sun className="w-6 h-6" />
                                            <span className="text-sm">Light</span>
                                        </button>
                                        <button
                                            onClick={() => updateAppearanceSetting('theme', 'dark')}
                                            className={`p-3 border rounded-lg flex flex-col items-center gap-2 transition-colors ${settings.appearance.theme === 'dark'
                                                ? 'border-primary bg-primary/10'
                                                : 'border-border hover:bg-muted'
                                                }`}
                                        >
                                            <Moon className="w-6 h-6" />
                                            <span className="text-sm">Dark</span>
                                        </button>
                                        <button
                                            onClick={() => updateAppearanceSetting('theme', 'system')}
                                            className={`p-3 border rounded-lg flex flex-col items-center gap-2 transition-colors ${settings.appearance.theme === 'system'
                                                ? 'border-primary bg-primary/10'
                                                : 'border-border hover:bg-muted'
                                                }`}
                                        >
                                            <Monitor className="w-6 h-6" />
                                            <span className="text-sm">System</span>
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-medium mb-2">Language</h4>
                                    <select
                                        value={settings.appearance.language}
                                        onChange={(e) => updateAppearanceSetting('language', e.target.value)}
                                        className="px-3 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary/50 transition-colors"
                                    >
                                        <option value="en">English</option>
                                        <option value="es">Español</option>
                                        <option value="fr">Français</option>
                                        <option value="de">Deutsch</option>
                                    </select>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {activeTab === 'security' && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Shield className="w-5 h-5" />
                                    Security Settings
                                </CardTitle>
                                <CardDescription>
                                    Manage your account security and authentication
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="font-medium">Two-Factor Authentication</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Add an extra layer of security to your account
                                            </p>
                                        </div>
                                        <Button
                                            variant={settings.security.twoFactorEnabled ? "default" : "outline"}
                                            size="sm"
                                            onClick={() => updateSecuritySetting('twoFactorEnabled', !settings.security.twoFactorEnabled)}
                                        >
                                            {settings.security.twoFactorEnabled ? 'Enabled' : 'Enable'}
                                        </Button>
                                    </div>

                                    <div>
                                        <h4 className="font-medium mb-2">Session Timeout</h4>
                                        <div className="flex items-center gap-2">
                                            <select
                                                value={settings.security.sessionTimeout}
                                                onChange={(e) => updateSecuritySetting('sessionTimeout', e.target.value)}
                                                className="px-3 py-2 border border-input bg-background text-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary/50 transition-colors"
                                            >
                                                <option value="15">15 minutes</option>
                                                <option value="30">30 minutes</option>
                                                <option value="60">1 hour</option>
                                                <option value="480">8 hours</option>
                                                <option value="never">Never</option>
                                            </select>
                                            <span className="text-sm text-muted-foreground">of inactivity</span>
                                        </div>
                                    </div>

                                    <div className="border-t pt-4">
                                        <h4 className="font-medium mb-2">Password</h4>
                                        <div className="flex items-center gap-4">
                                            <Button variant="outline" size="sm">
                                                Change Password
                                            </Button>
                                            <span className="text-sm text-muted-foreground">
                                                Last changed: Never
                                            </span>
                                        </div>
                                    </div>

                                    <div className="border-t pt-4">
                                        <h4 className="font-medium mb-2 text-red-600">Danger Zone</h4>
                                        <div className="space-y-3">
                                            <Button variant="outline" size="sm" className="border-destructive text-destructive hover:bg-destructive/10">
                                                Export Account Data
                                            </Button>
                                            <Button variant="outline" size="sm" className="border-destructive text-destructive hover:bg-destructive/10">
                                                Delete Account
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Save Button */}
                    <div className="flex justify-end">
                        <Button onClick={handleSave} disabled={isLoading}>
                            {isLoading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4 mr-2" />
                                    Save Settings
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
