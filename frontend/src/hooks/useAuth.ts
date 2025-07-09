/**
 * Authentication Hook
 * 
 * Custom React hook that provides a high-level interface for authentication
 * operations. Integrates the auth store, API calls, and error handling.
 * 
 * Features:
 * - Login/logout functionality
 * - User registration
 * - Password reset flow
 * - Session management
 * - Loading states
 * - Error handling
 * - Auto-logout on token expiration
 * - Remember me functionality
 * 
 * @example
 * ```typescript
 * import { useAuth } from '@/hooks/useAuth';
 * 
 * function LoginForm() {
 *   const { login, logout, user, isAuthenticated, isLoading, error } = useAuth();
 * 
 *   const handleLogin = async (data) => {
 *     await login(data);
 *   };
 * 
 *   return (
 *     <div>
 *       {isAuthenticated ? (
 *         <div>Welcome, {user?.name}!</div>
 *       ) : (
 *         <LoginForm onSubmit={handleLogin} />
 *       )}
 *     </div>
 *   );
 * }
 * ```
 */

import { useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/lib/store/authStore';
import { authApi } from '@/lib/api/auth';
import { tokenService } from '@/lib/auth/tokenService';
import { extractUserFromToken } from '@/lib/api/types';
import logger from '@/logger';
import type {
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthTokens,
    AuthUser,
    AuthError,
} from '@/lib/api/types';

/**
 * Authentication hook interface
 */
interface UseAuthReturn {
    // State
    user: AuthUser | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;

    // Actions
    login: (credentials: AuthLoginRequest, rememberMe?: boolean) => Promise<void>;
    register: (userData: AuthRegisterRequest) => Promise<void>;
    logout: () => Promise<void>;
    forgotPassword: (email: string) => Promise<void>;
    resetPassword: (token: string, newPassword: string) => Promise<void>;
    clearError: () => void;
    refreshSession: () => Promise<boolean>;

    // Utilities
    hasRole: (role: string) => boolean;
    hasAnyRole: (roles: string[]) => boolean;
    isSessionValid: () => boolean;
}

/**
 * Custom hook for authentication operations
 */
export function useAuth(): UseAuthReturn {
    const navigate = useNavigate();
    const {
        user,
        tokens,
        isAuthenticated,
        isLoading,
        error,
        login: storeLogin,
        logout: storeLogout,
        setLoading,
        setError,
        clearError: storeClearError,
        setTokens,
        setRefreshing,
    } = useAuthStore();

    /**
     * Login user with credentials
     */
    const login = useCallback(async (
        credentials: AuthLoginRequest,
        rememberMe: boolean = false
    ): Promise<void> => {
        logger.info('User login attempt', { email: credentials.email, rememberMe });

        try {
            setLoading(true);
            storeClearError();

            // Call API for authentication
            const authResponse = await authApi.login(credentials);

            // Extract user from tokens
            const userData = extractUserFromToken(authResponse);
            if (!userData) {
                throw new Error('Invalid authentication response');
            }

            // Store authentication data
            storeLogin(userData, authResponse);

            // Store remember me preference
            if (rememberMe) {
                localStorage.setItem('auth_remember_me', 'true');
            } else {
                localStorage.removeItem('auth_remember_me');
            }

            logger.info('User login successful', {
                userId: userData.id,
                email: userData.email,
                rememberMe
            });

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Login failed';
            logger.error('User login failed', {
                email: credentials.email,
                error: errorMessage
            });
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [storeLogin, setLoading, setError, storeClearError]);

    /**
     * Register new user
     */
    const register = useCallback(async (
        userData: AuthRegisterRequest
    ): Promise<void> => {
        logger.info('User registration attempt', { email: userData.email, name: userData.name });

        try {
            setLoading(true);
            storeClearError();

            // Call API for registration
            const authResponse = await authApi.register(userData);

            // Extract user from tokens
            const userInfo = extractUserFromToken(authResponse);
            if (!userInfo) {
                throw new Error('Invalid registration response');
            }

            // Store authentication data
            storeLogin(userInfo, authResponse);

            logger.info('User registration successful', {
                userId: userInfo.id,
                email: userInfo.email
            });

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Registration failed';
            logger.error('User registration failed', {
                email: userData.email,
                error: errorMessage
            });
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [storeLogin, setLoading, setError, storeClearError]);

    /**
     * Logout user
     */
    const logout = useCallback(async (): Promise<void> => {
        logger.info('User logout initiated');

        try {
            setLoading(true);

            // Call logout API if we have valid tokens
            if (tokens?.access_token) {
                try {
                    await authApi.logout();
                    logger.info('Server logout successful');
                } catch (error) {
                    // Continue with local logout even if server logout fails
                    logger.warn('Server logout failed, continuing with local logout', { error });
                }
            }

            // Clear local state
            storeLogout();

            // Clear token service state
            tokenService.clearRefreshState();

            // Clear remember me preference
            localStorage.removeItem('auth_remember_me');

            logger.info('User logout completed');

        } catch (error) {
            logger.error('Logout failed', { error });
            // Still perform local logout on error
            storeLogout();
        } finally {
            setLoading(false);
        }
    }, [tokens, storeLogout, setLoading]);

    /**
     * Initiate forgot password flow
     */
    const forgotPassword = useCallback(async (email: string): Promise<void> => {
        logger.info('Forgot password initiated', { email });

        try {
            setLoading(true);
            storeClearError();

            await authApi.forgotPassword({ email });

            logger.info('Forgot password email sent', { email });

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to send reset email';
            logger.error('Forgot password failed', { email, error: errorMessage });
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [setLoading, setError, storeClearError]);

    /**
     * Reset password with token
     */
    const resetPassword = useCallback(async (
        token: string,
        newPassword: string
    ): Promise<void> => {
        logger.info('Password reset initiated');

        try {
            setLoading(true);
            storeClearError();

            await authApi.resetPassword({ token, new_password: newPassword });

            logger.info('Password reset successful');

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Password reset failed';
            logger.error('Password reset failed', { error: errorMessage });
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [setLoading, setError, storeClearError]);

    /**
     * Clear authentication error
     */
    const clearError = useCallback(() => {
        storeClearError();
    }, [storeClearError]);

    /**
     * Refresh user session
     */
    const refreshSession = useCallback(async (): Promise<boolean> => {
        logger.info('Session refresh initiated');

        try {
            if (!tokens?.refresh_token) {
                logger.warn('No refresh token available for session refresh');
                return false;
            }

            setRefreshing(true);

            // Use token service to refresh
            const newAccessToken = await tokenService.refreshAccessToken();

            if (!newAccessToken) {
                logger.warn('Session refresh failed - no new token received');
                return false;
            }

            logger.info('Session refresh successful');
            return true;

        } catch (error) {
            logger.error('Session refresh failed', { error });
            // Auto-logout on refresh failure
            await logout();
            return false;
        } finally {
            setRefreshing(false);
        }
    }, [tokens, setRefreshing, logout]);

    /**
     * Check if user has specific role
     */
    const hasRole = useCallback((role: string): boolean => {
        if (!user || !user.roles) {
            return false;
        }
        return user.roles.includes(role);
    }, [user]);

    /**
     * Check if user has any of the specified roles
     */
    const hasAnyRole = useCallback((roles: string[]): boolean => {
        if (!user || !user.roles) {
            return false;
        }
        return roles.some(role => user.roles.includes(role));
    }, [user]);

    /**
     * Check if current session is valid
     */
    const isSessionValid = useCallback((): boolean => {
        if (!tokens?.access_token) {
            return false;
        }

        // Use token service to check expiration
        return !tokenService.needsRefresh();
    }, [tokens]);

    /**
     * Auto-logout on token expiration
     */
    useEffect(() => {
        if (!isAuthenticated || !tokens) {
            return;
        }

        // Check token expiration periodically
        const checkTokenExpiration = () => {
            if (tokenService.needsRefresh()) {
                logger.warn('Token expired, attempting refresh');
                refreshSession().catch(() => {
                    logger.error('Auto-refresh failed, logging out');
                });
            }
        };

        // Check every 5 minutes
        const interval = setInterval(checkTokenExpiration, 5 * 60 * 1000);

        return () => clearInterval(interval);
    }, [isAuthenticated, tokens, refreshSession]);

    /**
     * Initialize authentication state on mount
     */
    useEffect(() => {
        // This effect handles initialization logic if needed
        // The auth store handles token persistence automatically
        logger.debug('Authentication hook initialized', {
            isAuthenticated,
            hasUser: !!user
        });
    }, []);

    return {
        // State
        user,
        isAuthenticated,
        isLoading,
        error,

        // Actions
        login,
        register,
        logout,
        forgotPassword,
        resetPassword,
        clearError,
        refreshSession,

        // Utilities
        hasRole,
        hasAnyRole,
        isSessionValid,
    };
}

export default useAuth;
