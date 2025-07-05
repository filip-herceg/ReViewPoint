import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import UploadList from '@/components/UploadList'
import { useUploadStore } from '@/lib/store/uploadStore'

const globalAny: any = globalThis

describe('UploadList component', () => {
    beforeEach(() => {
        useUploadStore.setState({ uploads: [], currentUpload: null, loading: false, error: null })
        globalAny.fetch = vi.fn()
    })

    it('shows loading state', () => {
        act(() => {
            useUploadStore.setState({ loading: true })
        })
        render(<UploadList disableAutoFetch />)
        expect(screen.getByText(/loading uploads/i)).toBeInTheDocument()
    })

    it('shows error state', () => {
        act(() => {
            useUploadStore.setState({ error: 'fail', loading: false })
        })
        render(<UploadList disableAutoFetch />)
        expect(screen.getByText(/error: fail/i)).toBeInTheDocument()
    })

    it('shows empty state', () => {
        act(() => {
            useUploadStore.setState({ uploads: [], loading: false, error: null })
        })
        render(<UploadList disableAutoFetch />)
        expect(screen.getByText(/no uploads found/i)).toBeInTheDocument()
    })

    it('shows uploads', () => {
        act(() => {
            useUploadStore.setState({
                uploads: [
                    { id: '1', name: 'file.pdf', status: 'pending', progress: 0, createdAt: 'now' },
                    { id: '2', name: 'file2.pdf', status: 'completed', progress: 100, createdAt: 'now' },
                ],
                loading: false,
                error: null,
            })
        })
        render(<UploadList disableAutoFetch />)
        expect(screen.getByText('file.pdf')).toBeInTheDocument()
        expect(screen.getByText('file2.pdf')).toBeInTheDocument()
        expect(screen.getByText(/status: pending/i)).toBeInTheDocument()
        expect(screen.getByText(/status: completed/i)).toBeInTheDocument()
    })
})
