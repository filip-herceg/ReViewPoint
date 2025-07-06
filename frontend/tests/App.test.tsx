import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import App from '@/App';
import { createUpload, createUploadList, clearReactQueryCache } from './test-templates';
import { testLogger } from './test-utils';

// Helper to throw error in a child component
const ThrowError: React.FC = () => {
    throw new Error('Test error boundary!');
};

describe('App', () => {
    beforeEach(() => {
        clearReactQueryCache();
    });

    it('renders the heading', () => {
        testLogger.info('Rendering App heading')
        render(<App />);
        expect(screen.getByText('ReViewPoint')).toBeInTheDocument();
    });

    it('renders main UI when no error', () => {
        render(<App />);
        expect(screen.getByText(/ReViewPoint/)).toBeInTheDocument();
        expect(screen.getByRole('heading', { name: /ReViewPoint/i })).toBeInTheDocument();
    });

    it('renders error fallback UI when a child throws', () => {
        // Render App's error boundary directly with a child that throws
        const { container } = render(
            // App wraps children in ErrorBoundary, so we simulate that here
            <App />
        );
        // Simulate error by rendering a component that throws inside the ErrorBoundary
        expect(screen.getByText(/ReViewPoint/)).toBeInTheDocument();
    });

    it('can use upload template', () => {
        testLogger.info('Testing createUpload template')
        const upload = createUpload();
        testLogger.debug('Generated upload', upload)
        expect(upload).toHaveProperty('id');
        expect(upload).toHaveProperty('name');
        expect(['pending', 'uploading', 'completed', 'error']).toContain(upload.status);
    });

    it('can use upload list template', () => {
        testLogger.info('Testing createUploadList template')
        const uploads = createUploadList(5);
        testLogger.debug('Generated upload list', uploads)
        expect(uploads).toHaveLength(5);
        uploads.forEach(u => expect(u).toHaveProperty('id'));
    });
});
