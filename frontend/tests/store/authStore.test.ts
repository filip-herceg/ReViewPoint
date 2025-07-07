import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore, getToken } from '@/lib/store/authStore';
import { createTestError } from '../test-templates';

const user = { id: '1', username: 'test', email: 't@t.com', roles: ['user'] };

describe('authStore error handling', () => {
    beforeEach(() => {
        useAuthStore.setState({ user: null, token: null, isAuthenticated: false });
    });

    it('throws if login called with missing user', () => {
        expect(() => useAuthStore.getState().login(null as any, 'token')).toThrow(/user and token required/i);
    });

    it('throws if login called with missing token', () => {
        expect(() => useAuthStore.getState().login(user, null as any)).toThrow(/user and token required/i);
    });

    it('sets user, token, isAuthenticated on successful login', () => {
        useAuthStore.getState().login(user, 'token');
        const state = useAuthStore.getState();
        expect(state.user).toEqual(user);
        expect(state.token).toBe('token');
        expect(state.isAuthenticated).toBe(true);
    });

    it('clears user, token, isAuthenticated on logout', () => {
        useAuthStore.getState().login(user, 'token');
        useAuthStore.getState().logout();
        const state = useAuthStore.getState();
        expect(state.user).toBeNull();
        expect(state.token).toBeNull();
        expect(state.isAuthenticated).toBe(false);
    });

    it('getToken returns current token', () => {
        useAuthStore.getState().login(user, 'token');
        expect(getToken()).toBe('token');
        useAuthStore.getState().logout();
        expect(getToken()).toBeNull();
    });
});
