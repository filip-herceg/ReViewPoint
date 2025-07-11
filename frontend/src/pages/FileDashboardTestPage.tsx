import { useEffect, useState } from 'react';
import { FileManagementDashboard } from '@/components/file-management/FileManagementDashboard';
import { useFileManagementStore } from '@/lib/store/fileManagementStore';
import { Button } from '@/components/ui/button';

export default function FileDashboardTestPage() {
    const [message, setMessage] = useState<string | null>(null);
    const { bulkDelete, selectedFiles } = useFileManagementStore();

    const handleBulkDelete = async () => {
        try {
            if (selectedFiles.length === 0) {
                setMessage('No files selected for deletion');
                return;
            }

            const result = await bulkDelete(selectedFiles);
            setMessage(`Successfully deleted ${result.deleted.length} files. Failed: ${result.failed.length}`);
        } catch (error: any) {
            setMessage(`Error: ${error.message || 'Unknown error'}`);
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">File Dashboard Test</h1>

            {message && (
                <div className="mb-4 p-4 bg-blue-100 border border-blue-200 rounded-md">
                    {message}
                </div>
            )}

            <div className="mb-4">
                <Button onClick={handleBulkDelete} variant="destructive">
                    Test Bulk Delete
                </Button>
            </div>

            <div className="border rounded-md shadow">
                <FileManagementDashboard />
            </div>
        </div>
    );
}
