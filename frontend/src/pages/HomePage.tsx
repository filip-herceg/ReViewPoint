import React from 'react';
import UploadList from '@/components/UploadList';
import UploadForm from '@/components/UploadForm';
import { WebSocketStatus } from '@/components/websocket/WebSocketStatus';
import { Link } from 'react-router-dom';
import { useAuthStore } from '@/lib/store/authStore';
import { ArrowRight, Upload, FileText, BarChart3 } from 'lucide-react';

export default function HomePage() {
    const { isAuthenticated } = useAuthStore();

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                    Welcome to ReViewPoint
                </h1>
                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                    Upload your PDF documents and get comprehensive analysis and reviews
                    powered by advanced AI technology.
                </p>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <Upload className="h-8 w-8 text-blue-600 mb-3" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Easy Upload</h3>
                    <p className="text-gray-600">
                        Drag and drop your PDF files or browse to upload. Support for multiple file formats.
                    </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <FileText className="h-8 w-8 text-green-600 mb-3" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h3>
                    <p className="text-gray-600">
                        Get detailed analysis of your documents with AI-powered insights and recommendations.
                    </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <BarChart3 className="h-8 w-8 text-purple-600 mb-3" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Detailed Reports</h3>
                    <p className="text-gray-600">
                        View comprehensive reports with scores, feedback, and actionable insights.
                    </p>
                </div>
            </div>

            {/* Main Content Based on Auth Status */}
            {isAuthenticated ? (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-bold text-gray-900">Your Files</h2>
                        <Link
                            to="/uploads/new"
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                        >
                            <Upload className="h-4 w-4 mr-2" />
                            Upload New File
                        </Link>
                    </div>

                    {/* Upload Form */}
                    <UploadForm />

                    {/* Upload List */}
                    <UploadList />

                    {/* WebSocket Status Details */}
                    <div className="mt-6">
                        <WebSocketStatus showDetails />
                    </div>
                </div>
            ) : (
                <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        Get Started Today
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Sign up for a free account to start uploading and analyzing your documents.
                    </p>
                    <div className="flex justify-center space-x-4">
                        <Link
                            to="/auth/register"
                            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                        >
                            Get Started
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                        <Link
                            to="/auth/login"
                            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                        >
                            Login
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
}
