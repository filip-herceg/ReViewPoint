// Authentication-related types
// Maps to backend/src/schemas/auth.py

import type { MessageResponse } from './common';

/**
 * Token type literal
 * Matches backend TOKEN_TYPE_BEARER
 */
export type TokenType = 'bearer';

/**
 * Authentication tokens
 * Matches backend AuthResponse schema
 */
export interface AuthTokens {
    /** JWT access token */
    access_token: string;
    /** JWT refresh token */
    refresh_token: string;
    /** Token type (always 'bearer') */
    token_type: TokenType;
}

/**
 * User login request
 * Matches backend UserLoginRequest schema
 */
export interface AuthLoginRequest {
    /** User email address */
    email: string;
    /** User password */
    password: string;
}

/**
 * Login response
 * Same as AuthTokens but semantically different
 */
export interface AuthLoginResponse extends AuthTokens { }

/**
 * Logout response
 * Matches backend MessageResponse
 */
export interface AuthLogoutResponse extends MessageResponse { }

/**
 * User registration request
 * Matches backend UserRegisterRequest schema
 */
export interface AuthRegisterRequest {
    /** User email address */
    email: string;
    /** User password */
    password: string;
    /** User display name (optional) */
    name?: string;
}

/**
 * User registration response
 * Matches backend AuthResponse schema
 */
export interface AuthRegisterResponse extends AuthTokens { }

/**
 * Password reset request
 * Matches backend PasswordResetRequest schema
 */
export interface AuthPasswordResetRequest {
    /** User email address */
    email: string;
}

/**
 * Password reset response
 * Matches backend MessageResponse
 */
export interface AuthPasswordResetResponse extends MessageResponse { }

/**
 * Password reset confirmation request
 * Matches backend PasswordResetConfirmRequest schema
 */
export interface AuthPasswordResetConfirmRequest {
    /** Reset token */
    token: string;
    /** New password */
    new_password: string;
}

/**
 * Password reset confirmation response
 * Matches backend MessageResponse
 */
export interface AuthPasswordResetConfirmResponse extends MessageResponse { }

/**
 * Token refresh response
 * Matches backend AuthResponse schema
 */
export interface AuthTokenRefreshResponse extends AuthTokens { }

/**
 * JWT token payload structure
 * Decoded access token content
 */
export interface JWTPayload {
    /** User ID */
    sub: string;
    /** User email */
    email: string;
    /** Token expiration (Unix timestamp) */
    exp: number;
    /** Token issued at (Unix timestamp) */
    iat: number;
    /** Token issuer */
    iss?: string;
    /** Token audience */
    aud?: string;
    /** User roles/permissions */
    roles?: string[];
}

/**
 * Authentication state
 * Used by auth store and components
 */
export interface AuthState {
    /** Whether user is authenticated */
    isAuthenticated: boolean;
    /** Authentication tokens */
    tokens: AuthTokens | null;
    /** Current user info from token */
    user: AuthUser | null;
    /** Whether auth is being initialized */
    isLoading: boolean;
    /** Last authentication error */
    error: string | null;
}

/**
 * User information from auth token
 * Subset of full user profile
 */
export interface AuthUser {
    /** User ID (from JWT sub claim) */
    id: string;
    /** User email */
    email: string;
    /** User display name */
    name?: string;
    /** User roles */
    roles: string[];
}

/**
 * Authentication error types
 */
export enum AuthErrorType {
    INVALID_CREDENTIALS = 'invalid_credentials',
    TOKEN_EXPIRED = 'token_expired',
    TOKEN_INVALID = 'token_invalid',
    USER_NOT_FOUND = 'user_not_found',
    USER_ALREADY_EXISTS = 'user_already_exists',
    PASSWORD_TOO_WEAK = 'password_too_weak',
    EMAIL_INVALID = 'email_invalid',
    RATE_LIMITED = 'rate_limited',
    REFRESH_TOKEN_BLACKLISTED = 'refresh_token_blacklisted',
    REFRESH_TOKEN_RATE_LIMITED = 'refresh_token_rate_limited',
    SERVER_ERROR = 'server_error',
    NETWORK_ERROR = 'network_error',
    UNKNOWN = 'unknown',
}

/**
 * Authentication error
 */
export interface AuthError {
    /** Error type */
    type: AuthErrorType;
    /** Error message */
    message: string;
    /** HTTP status code */
    status?: number;
    /** Additional error details */
    details?: Record<string, unknown>;
}

/**
 * Password validation requirements
 * Matches backend validation rules
 */
export interface PasswordRequirements {
    /** Minimum length */
    minLength: number;
    /** Maximum length */
    maxLength: number;
    /** Requires uppercase letter */
    requiresUppercase: boolean;
    /** Requires lowercase letter */
    requiresLowercase: boolean;
    /** Requires number */
    requiresNumber: boolean;
    /** Requires special character */
    requiresSpecial: boolean;
}

/**
 * Default password requirements
 * Matches backend validation - requires at least one letter AND one digit
 */
export const DEFAULT_PASSWORD_REQUIREMENTS: PasswordRequirements = {
    minLength: 8,
    maxLength: 128,
    requiresUppercase: false,    // Backend doesn't specifically require uppercase
    requiresLowercase: false,    // Backend doesn't specifically require lowercase 
    requiresNumber: true,        // Backend requires at least one digit
    requiresSpecial: false,      // Backend doesn't require special characters
};

/**
 * Email validation pattern
 * Matches backend email validation (EmailStr from Pydantic)
 * Supports: alphanumeric, dots, hyphens, underscores, and plus signs
 * Prevents consecutive dots and other invalid patterns
 */
export const EMAIL_REGEX = /^[a-zA-Z0-9._+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$/;

/**
 * Type guard for AuthTokens
 */
export function isAuthTokens(value: unknown): value is AuthTokens {
    return (
        typeof value === 'object' &&
        value !== null &&
        'access_token' in value &&
        'refresh_token' in value &&
        'token_type' in value &&
        typeof (value as any).access_token === 'string' &&
        typeof (value as any).refresh_token === 'string' &&
        (value as any).token_type === 'bearer'
    );
}

/**
 * Type guard for AuthError
 */
export function isAuthError(error: unknown): error is AuthError {
    return (
        typeof error === 'object' &&
        error !== null &&
        'type' in error &&
        'message' in error &&
        Object.values(AuthErrorType).includes((error as any).type)
    );
}

/**
 * Utility to decode JWT payload (without verification)
 * For client-side display purposes only
 * @param token - JWT token to decode
 * @returns Decoded payload or null if invalid
 */
export function decodeJWTPayload(token: string): JWTPayload | null {
    if (!token || typeof token !== 'string') {
        return null;
    }

    try {
        const parts = token.split('.');
        if (parts.length !== 3) {
            return null;
        }

        const payload = parts[1];
        if (!payload) {
            return null;
        }

        const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
        return JSON.parse(decoded) as JWTPayload;
    } catch {
        // Return null for any decoding errors
        return null;
    }
}

/**
 * Check if token is expired (client-side check only)
 */
export function isTokenExpired(payload: JWTPayload): boolean {
    if (!payload || !payload.exp) {
        return true;
    }

    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
}

/**
 * Extract user info from access token
 */
export function extractUserFromToken(tokens: AuthTokens): AuthUser | null {
    try {
        if (!tokens.access_token) {
            return null;
        }

        const payload = decodeJWTPayload(tokens.access_token);
        if (!payload || !payload.sub || !payload.email) {
            return null;
        }

        return {
            id: payload.sub,
            email: payload.email,
            name: undefined, // Not included in token by default
            roles: payload.roles || [],
        };
    } catch {
        return null;
    }
}
