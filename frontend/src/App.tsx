import React from 'react';

import UploadList from '@/components/UploadList';
import UploadForm from '@/components/UploadForm';

export default function App() {
    return (
        <div className="p-4 max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">ReViewPoint</h1>
            <UploadForm />
            <UploadList />
        </div>
    );
}
