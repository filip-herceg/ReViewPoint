import { useUploadStore } from '@/lib/store/uploadStore'
import { act } from 'react-dom/test-utils'
import { createTestError } from '../../tests/test-templates'

describe('uploadStore error handling', () => {
    beforeEach(() => {
        // Reset store state before each test
        act(() => {
            useUploadStore.setState({
                uploads: [],
                currentUpload: null,
                loading: false,
                error: null,
            })
        })
    })

    it('throws and sets error for invalid addUpload', () => {
        expect(() => useUploadStore.getState().addUpload(null as any)).toThrow()
    })

    it('throws and sets error for invalid updateUpload', () => {
        expect(() => useUploadStore.getState().updateUpload(undefined as any, {})).toThrow()
    })

    it('throws and sets error for invalid setCurrentUpload', () => {
        expect(() => useUploadStore.getState().setCurrentUpload({} as any)).toThrow()
    })

    it('sets error on fetchUploads API error', async () => {
        // Mock api.getUploads to return error
        const { api } = await import('@/lib/api/api');
        api.getUploads = vi.fn().mockResolvedValue({ error: 'fail' });
        await act(async () => {
            await useUploadStore.getState().fetchUploads();
        });
        expect(useUploadStore.getState().error).toBeTruthy();
        expect(useUploadStore.getState().error?.message).toMatch(/fail/);
    })

    it('sets error on createUpload API error', async () => {
        const { api } = await import('@/lib/api/api');
        api.createUpload = vi.fn().mockResolvedValue({ error: 'fail' });
        await act(async () => {
            await useUploadStore.getState().createUpload({ name: 'foo', status: 'pending', progress: 0 });
        });
        expect(useUploadStore.getState().error).toBeTruthy();
        expect(useUploadStore.getState().error?.message).toMatch(/fail/);
    })

    it('sets error for invalid createUpload input', async () => {
        await useUploadStore.getState().createUpload({} as any);
        expect(useUploadStore.getState().error).toBeTruthy();
    })

    it('sets error on patchUpload API error', async () => {
        const { api } = await import('@/lib/api/api');
        api.updateUpload = vi.fn().mockResolvedValue({ error: 'fail' });
        await act(async () => {
            await useUploadStore.getState().patchUpload('id', { name: 'bar' });
        });
        expect(useUploadStore.getState().error).toBeTruthy();
        expect(useUploadStore.getState().error?.message).toMatch(/fail/);
    })

    it('sets error for invalid patchUpload input', async () => {
        await useUploadStore.getState().patchUpload(undefined as any, {});
        expect(useUploadStore.getState().error).toBeTruthy();
    })

    it('sets error on removeUpload API error', async () => {
        const { api } = await import('@/lib/api/api');
        api.deleteUpload = vi.fn().mockResolvedValue({ error: 'fail' });
        await act(async () => {
            await useUploadStore.getState().removeUpload('id');
        });
        expect(useUploadStore.getState().error).toBeTruthy();
        expect(useUploadStore.getState().error?.message).toMatch(/fail/);
    })

    it('sets error for invalid removeUpload input', async () => {
        await useUploadStore.getState().removeUpload(undefined as any);
        expect(useUploadStore.getState().error).toBeTruthy();
    })
})
