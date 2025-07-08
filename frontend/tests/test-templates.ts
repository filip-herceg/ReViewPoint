// Utility: Create a test error object for error handling tests
export function createTestError(message: string | Error = 'Test error'): Error {
    // If the message is already an Error, return it directly instead of wrapping it
    if (message instanceof Error) {
        testLogger.debug('Returning existing error object', message);
        return message;
    }

    const err = new Error(message);
    testLogger.debug('Created test error object', err);
    return err;
}
// Centralized test data templates (factories) for frontend tests
// Use these to generate consistent test data in all tests
// You can import utilities from test-utils as needed

import { randomString, randomInt, randomDate, testLogger } from './test-utils';
import { QueryClient } from '@tanstack/react-query';
import type {
    User,
    AuthTokens,
    AuthRegisterRequest,
    AuthLoginRequest,
    AuthError,
    UserUpdateRequest,
    Upload,
    FileUploadResponse,
    ApiResponse,
    ApiError,
    PaginatedResponse,
} from '@/lib/api/types';

// Utility to clear all react-query caches for test isolation
export function clearReactQueryCache() {
    // If you use a global QueryClient, clear it here. Otherwise, clear all caches in your test setup.
    // This is a no-op placeholder for now, but you can call this in beforeEach/afterEach in tests.
    // If you use a custom QueryClient instance, call queryClient.clear() in your test file.
    // Example:
    // queryClient.clear();
    // For global cache: QueryClient.clear();
    // (No-op for now)
    testLogger.info('Cleared react-query cache (noop placeholder)');
}

// Update Upload type to match app (pending | uploading | completed | error)
export type TestUpload = {
    id: string;
    name: string;
    status: 'pending' | 'uploading' | 'completed' | 'error';
    progress: number;
    createdAt: string;
};

import { randomStatus } from './test-utils';

// Pick a random status for TestUpload
export function randomUploadStatus(): TestUpload['status'] {
    const statuses: TestUpload['status'][] = ['pending', 'uploading', 'completed', 'error'];
    const status = statuses[randomInt(0, statuses.length - 1)];
    if (status === 'error') {
        testLogger.warn('Picked random upload status: error');
    } else {
        testLogger.debug('Picked random upload status:', status);
    }
    return status;
}

export function createUpload(overrides: Partial<TestUpload> = {}): TestUpload {
    const upload: TestUpload = {
        id: overrides.id || randomString(6),
        name: overrides.name || `${randomString(4)}.pdf`,
        status: overrides.status || randomUploadStatus(),
        progress: overrides.progress ?? randomInt(0, 100),
        createdAt: overrides.createdAt || randomDate(),
        ...overrides,
    };
    if (upload.status === 'error') {
        testLogger.error('Created upload with error status', upload);
    } else if (upload.progress === 0) {
        testLogger.info('Created upload with 0% progress', upload);
    } else {
        testLogger.debug('Created upload object', upload);
    }
    return upload;

}


// Create an array of uploads (for UploadList tests)
export function createUploadList(count = 3, overrides: Partial<TestUpload> = {}): TestUpload[] {
    const list = Array.from({ length: count }, () => createUpload(overrides));
    if (count > 10) {
        testLogger.warn(`Created large upload list of length ${count}`);
    } else {
        testLogger.info(`Created upload list of length ${count}`, list);
    }
    return list;
}

// If you add user/auth features, add user templates here
// export function createUser(...) { ... }

export function createUser(overrides: Partial<User> = {}): User {
    const user: User = {
        id: overrides.id ?? Math.floor(Math.random() * 10000),
        email: overrides.email ?? randomString(5) + '@example.com',
        name: overrides.name ?? ('user_' + randomString(4)),
        bio: overrides.bio ?? null,
        avatar_url: overrides.avatar_url ?? null,
        created_at: overrides.created_at ?? new Date().toISOString(),
        updated_at: overrides.updated_at ?? new Date().toISOString(),
    };
    if (user.name && user.name.includes('admin')) {
        testLogger.info('Created admin user', user);
    } else {
        testLogger.debug('Created user', user);
    }
    return user;
}

// Template for upload form data (matches UploadForm initial state)
export type UploadFormData = {
    name: string;
    status: 'pending';
    progress: number;
};

export function createUploadFormData(overrides: Partial<UploadFormData> = {}): UploadFormData {
    const formData: UploadFormData = {
        ...overrides,
        name: overrides.name || randomString(8) + '.pdf',
        progress: 0,
        status: 'pending', // Always force status to 'pending' to satisfy UploadFormData type
    };
    if (formData.name.endsWith('.pdf')) {
        testLogger.debug('Created upload form data for PDF', formData);
    } else {
        testLogger.info('Created upload form data', formData);
    }
    return formData;
}

// If you add forms, add form data templates here
// export function createUploadFormData(...) { ... }

// Template for plausible analytics event
export type AnalyticsEvent = {
    name: string;
    props?: Record<string, any>;
};

export function createAnalyticsEvent(overrides: Partial<AnalyticsEvent> = {}): AnalyticsEvent {
    const event = {
        name: overrides.name || 'test_event_' + randomString(5),
        props: overrides.props || { foo: randomString(3) },
        ...overrides,
    };
    if (event.name.startsWith('test_event_')) {
        testLogger.debug('Created test analytics event', event);
    } else {
        testLogger.info('Created analytics event', event);
    }
    return event;
}

// Template for button props (for UI tests)
export type ButtonProps = {
    variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
    size?: 'default' | 'sm' | 'lg' | 'icon';
    className?: string;
    children?: string;
    asChild?: boolean;
    [key: string]: any;
};

export function createButtonProps(overrides: Partial<ButtonProps> = {}): ButtonProps {
    const variants = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'] as const;
    const sizes = ['default', 'sm', 'lg', 'icon'] as const;
    const btn = {
        variant: overrides.variant || variants[randomInt(0, variants.length - 1)],
        size: overrides.size || sizes[randomInt(0, sizes.length - 1)],
        className: overrides.className || '',
        children: overrides.children || 'Button',
        asChild: overrides.asChild ?? false,
        ...overrides,
    };
    if (btn.variant === 'destructive') {
        testLogger.warn('Created destructive button props', btn);
    } else {
        testLogger.debug('Created button props', btn);
    }
    return btn;
}

// Template for input props (for UI tests)
export type InputProps = {
    className?: string;
    type?: string;
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    [key: string]: any;
};

export function createInputProps(overrides: Partial<InputProps> = {}): InputProps {
    const types = ['text', 'email', 'password', 'number', 'file'] as const;
    const input = {
        className: overrides.className || '',
        type: overrides.type || types[randomInt(0, types.length - 1)],
        value: overrides.value || randomString(8),
        placeholder: overrides.placeholder || 'Enter value',
        disabled: overrides.disabled ?? false,
        ...overrides,
    };
    if (input.type === 'password') {
        testLogger.info('Created password input props', input);
    } else {
        testLogger.debug('Created input props', input);
    }
    return input;
}

// Template for card props (for UI tests)
export type CardProps = {
    className?: string;
    children?: React.ReactNode;
    [key: string]: any;
};

export function createCardProps(overrides: Partial<CardProps> = {}): CardProps {
    const card = {
        className: overrides.className || '',
        children: overrides.children || 'Card Content',
        ...overrides,
    };
    if (card.className && card.className.includes('highlight')) {
        testLogger.info('Created highlighted card props', card);
    } else {
        testLogger.debug('Created card props', card);
    }
    return card;
}

// API Types Templates
// Templates for testing API types and responses

import {
    AuthErrorType,
} from '@/lib/api/types';

// Auth Templates
export function createAuthTokens(overrides: Partial<AuthTokens> = {}): AuthTokens {
    const tokens: AuthTokens = {
        access_token: overrides.access_token || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + randomString(32),
        refresh_token: overrides.refresh_token || 'refresh_' + randomString(32),
        token_type: 'bearer',
        ...overrides,
    };
    testLogger.debug('Created auth tokens', {
        access_token: tokens.access_token.substring(0, 20) + '...',
        refresh_token: tokens.refresh_token.substring(0, 20) + '...',
        token_type: tokens.token_type
    });
    return tokens;
}

export function createAuthRegisterRequest(overrides: Partial<AuthRegisterRequest> = {}): AuthRegisterRequest {
    const request: AuthRegisterRequest = {
        email: overrides.email || randomString(5) + '@example.com',
        password: overrides.password || 'securePassword' + randomString(3),
        name: overrides.name || 'User ' + randomString(4),
        ...overrides,
    };
    testLogger.debug('Created auth register request', { email: request.email, name: request.name });
    return request;
}

export function createAuthLoginRequest(overrides: Partial<AuthLoginRequest> = {}): AuthLoginRequest {
    const request: AuthLoginRequest = {
        email: overrides.email || randomString(5) + '@example.com',
        password: overrides.password || 'password123',
        ...overrides,
    };
    testLogger.debug('Created auth login request', { email: request.email });
    return request;
}

export function createAuthError(
    type: AuthErrorType = AuthErrorType.INVALID_CREDENTIALS,
    overrides: Partial<AuthError> = {}
): AuthError {
    const error: AuthError = {
        type,
        message: overrides.message || `Auth error: ${type}`,
        status: overrides.status || (type === AuthErrorType.TOKEN_EXPIRED ? 401 : 400),
        details: overrides.details,
        ...overrides,
    };
    testLogger.error('Created auth error', error);
    return error;
}

// User Templates
export function createApiUser(overrides: Partial<User> = {}): User {
    const user: User = {
        id: overrides.id || randomInt(1, 10000),
        email: overrides.email || randomString(5) + '@example.com',
        name: overrides.name || 'User ' + randomString(4),
        bio: overrides.bio || null,
        avatar_url: overrides.avatar_url || null,
        created_at: overrides.created_at || randomDate(),
        updated_at: overrides.updated_at || randomDate(),
        ...overrides,
    };
    testLogger.debug('Created API user', { id: user.id, email: user.email, name: user.name });
    return user;
}

export function createUserUpdateRequest(overrides: Partial<UserUpdateRequest> = {}): UserUpdateRequest {
    const request: UserUpdateRequest = {
        name: overrides.name !== undefined ? overrides.name : 'Updated User ' + randomString(3),
        bio: overrides.bio !== undefined ? overrides.bio : 'Updated bio ' + randomString(5),
        ...overrides,
    };
    testLogger.debug('Created user update request', request);
    return request;
}

// Upload Templates
export function createApiUpload(overrides: Partial<Upload> = {}): Upload {
    const statuses: Upload['status'][] = ['pending', 'uploading', 'completed', 'error', 'cancelled'];
    const upload: Upload = {
        id: overrides.id || randomString(8),
        name: overrides.name || randomString(5) + '.pdf',
        status: overrides.status || statuses[randomInt(0, statuses.length - 1)],
        progress: overrides.progress ?? (overrides.status === 'completed' ? 100 : randomInt(0, 99)),
        createdAt: overrides.createdAt || randomDate(),
        size: overrides.size || randomInt(1024, 10 * 1024 * 1024), // 1KB to 10MB
        type: overrides.type || 'application/pdf',
        ...overrides,
    };

    if (upload.status === 'error') {
        testLogger.warn('Created API upload with error status', upload);
    } else {
        testLogger.debug('Created API upload', upload);
    }
    return upload;
}

export function createFileUploadResponse(overrides: Partial<FileUploadResponse> = {}): FileUploadResponse {
    const response: FileUploadResponse = {
        filename: overrides.filename || randomString(5) + '.pdf',
        url: overrides.url || '/uploads/' + randomString(8) + '.pdf',
        ...overrides,
    };
    testLogger.debug('Created file upload response', response);
    return response;
}

// Generic API Response Templates
export function createApiResponse<T>(data: T, overrides: Partial<ApiResponse<T>> = {}): ApiResponse<T> {
    const response: ApiResponse<T> = {
        data,
        error: overrides.error,
        ...overrides,
    };

    if (response.error) {
        testLogger.error('Created API error response', { error: response.error });
    } else {
        testLogger.debug('Created API success response', { dataType: typeof data });
    }
    return response;
}

export function createApiErrorResponse(error: string): ApiResponse<never> {
    const response: ApiResponse<never> = {
        data: null,
        error,
    };
    testLogger.error('Created API error response', response);
    return response;
}

export function createPaginatedResponse<T>(
    items: T[],
    overrides: Partial<PaginatedResponse<T>> = {}
): PaginatedResponse<T> {
    const total = overrides.total || items.length;
    const per_page = overrides.per_page || 10;
    const page = overrides.page || 1;
    const pages = Math.ceil(total / per_page);

    const response: PaginatedResponse<T> = {
        items,
        total,
        page,
        per_page,
        pages,
        ...overrides,
    };

    testLogger.debug('Created paginated response', {
        itemCount: items.length,
        total,
        page,
        pages
    });
    return response;
}

// Validation Error Templates
export function createValidationError(field: string, message: string, code?: string): ApiError {
    const error: ApiError = {
        message: 'Validation failed',
        type: 'validation_error',
        field_errors: [
            {
                field,
                message,
                code,
            },
        ],
    };
    testLogger.error('Created validation error', error);
    return error;
}

export function createNetworkError(): ApiError {
    const error: ApiError = {
        message: 'Network error occurred',
        type: 'network_error',
        details: {
            code: 'NETWORK_ERROR',
            timestamp: new Date().toISOString(),
        },
    };
    testLogger.error('Created network error', error);
    return error;
}

// Enhanced Auth Token Templates for JWT Testing

// Create expired auth tokens for testing refresh scenarios
export function createExpiredAuthTokens(overrides: Partial<AuthTokens> = {}): AuthTokens {
    const now = Math.floor(Date.now() / 1000);
    const exp = now - 3600; // 1 hour ago (expired)

    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({
        sub: randomInt(1, 1000).toString(),
        email: `user${randomString(4)}@example.com`,
        exp,
        iat: now - 7200, // 2 hours ago
        iss: 'reviewpoint',
        roles: ['user']
    }));
    const signature = randomString(43);

    const tokens: AuthTokens = {
        access_token: overrides.access_token || `${header}.${payload}.${signature}`,
        refresh_token: overrides.refresh_token || `rt_${randomString(64)}`,
        token_type: 'bearer',
        ...overrides,
    };
    testLogger.debug('Created expired auth tokens', {
        hasAccessToken: !!tokens.access_token,
        hasRefreshToken: !!tokens.refresh_token,
        expiry: exp
    });
    return tokens;
}

// Create tokens that will expire soon (for testing refresh buffer)
export function createSoonToExpireAuthTokens(overrides: Partial<AuthTokens> = {}): AuthTokens {
    const now = Math.floor(Date.now() / 1000);
    const exp = now + 60; // 1 minute from now (within refresh buffer)

    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({
        sub: randomInt(1, 1000).toString(),
        email: `user${randomString(4)}@example.com`,
        exp,
        iat: now - 60, // 1 minute ago
        iss: 'reviewpoint',
        roles: ['user']
    }));
    const signature = randomString(43);

    const tokens: AuthTokens = {
        access_token: overrides.access_token || `${header}.${payload}.${signature}`,
        refresh_token: overrides.refresh_token || `rt_${randomString(64)}`,
        token_type: 'bearer',
        ...overrides,
    };
    testLogger.debug('Created soon-to-expire auth tokens', {
        hasAccessToken: !!tokens.access_token,
        hasRefreshToken: !!tokens.refresh_token,
        expiry: exp,
        timeToExpiry: exp - now
    });
    return tokens;
}

// Create valid long-lived auth tokens (for testing normal scenarios)
export function createValidAuthTokens(overrides: Partial<AuthTokens> = {}): AuthTokens {
    const now = Math.floor(Date.now() / 1000);
    const exp = now + 3600; // 1 hour from now

    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({
        sub: randomInt(1, 1000).toString(),
        email: `user${randomString(4)}@example.com`,
        exp,
        iat: now,
        iss: 'reviewpoint',
        roles: ['user']
    }));
    const signature = randomString(43);

    const tokens: AuthTokens = {
        access_token: overrides.access_token || `${header}.${payload}.${signature}`,
        refresh_token: overrides.refresh_token || `rt_${randomString(64)}`,
        token_type: 'bearer',
        ...overrides,
    };
    testLogger.debug('Created valid auth tokens', {
        hasAccessToken: !!tokens.access_token,
        hasRefreshToken: !!tokens.refresh_token,
        expiry: exp,
        timeToExpiry: exp - now
    });
    return tokens;
}

// Token Refresh Test Templates
export function createTokenRefreshRequest(refreshToken?: string) {
    const request = {
        refresh_token: refreshToken || `rt_${randomString(64)}`
    };
    testLogger.debug('Created token refresh request', {
        hasRefreshToken: !!request.refresh_token
    });
    return request;
}

export function createTokenRefreshResponse(overrides: Partial<AuthTokens> = {}): AuthTokens {
    const tokens = createValidAuthTokens(overrides);
    testLogger.debug('Created token refresh response', {
        hasAccessToken: !!tokens.access_token,
        hasRefreshToken: !!tokens.refresh_token
    });
    return tokens;
}

// Mock token service state for testing
export function createTokenServiceMockState() {
    return {
        isRefreshing: false,
        refreshPromise: null,
        refreshQueue: [],
    };
}
