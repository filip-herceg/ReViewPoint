import { describe, it, expect, beforeEach } from 'vitest';
import { useUIStore } from '@/lib/store/uiStore';

describe('uiStore error handling', () => {
    beforeEach(() => {
        useUIStore.setState({ theme: 'light', sidebarOpen: false, notifications: [] });
    });

    it('throws if setTheme called with invalid theme', () => {
        expect(() => useUIStore.getState().setTheme('blue' as any)).toThrow(/invalid theme/i);
    });

    it('sets theme for valid values', () => {
        useUIStore.getState().setTheme('dark');
        expect(useUIStore.getState().theme).toBe('dark');
        useUIStore.getState().setTheme('light');
        expect(useUIStore.getState().theme).toBe('light');
    });

    it('toggles sidebar', () => {
        const prev = useUIStore.getState().sidebarOpen;
        useUIStore.getState().toggleSidebar();
        expect(useUIStore.getState().sidebarOpen).toBe(!prev);
    });

    it('throws if addNotification called with empty message', () => {
        expect(() => useUIStore.getState().addNotification('')).toThrow(/notification message required/i);
    });

    it('adds notification for valid message', () => {
        useUIStore.getState().addNotification('Hello');
        expect(useUIStore.getState().notifications).toContain('Hello');
    });

    it('throws if removeNotification called with invalid index', () => {
        useUIStore.getState().addNotification('A');
        expect(() => useUIStore.getState().removeNotification(-1)).toThrow(/invalid notification index/i);
        expect(() => useUIStore.getState().removeNotification(99)).toThrow(/invalid notification index/i);
    });

    it('removes notification for valid index', () => {
        useUIStore.getState().addNotification('A');
        useUIStore.getState().addNotification('B');
        useUIStore.getState().removeNotification(0);
        expect(useUIStore.getState().notifications).toEqual(['B']);
    });
});
