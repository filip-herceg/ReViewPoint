// Common types and utilities for API communication
// These types are shared across all API modules

import type { AxiosError } from 'axios';

/**
 * HTTP Status Code enumeration for type safety
 */
export enum HttpStatusCode {
    // Success
    OK = 200,
    CREATED = 201,
    ACCEPTED = 202,
    NO_CONTENT = 204,

    // Client Errors
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    CONFLICT = 409,
    UNPROCESSABLE_ENTITY = 422,

    // Server Errors
    INTERNAL_SERVER_ERROR = 500,
    BAD_GATEWAY = 502,
    SERVICE_UNAVAILABLE = 503,
}

/**
 * Standard API response wrapper
 * Matches FastAPI response patterns
 */
export interface ApiResponse<T = unknown> {
    /** Response data - null on error */
    data: T | null;
    /** Error message - undefined on success */
    error?: string;
}

/**
 * Paginated response wrapper
 * Matches backend pagination patterns
 */
export interface PaginatedResponse<T> {
    /** Array of items */
    items: T[];
    /** Total number of items available */
    total: number;
    /** Current page number (1-based) */
    page: number;
    /** Number of items per page */
    per_page: number;
    /** Total number of pages */
    pages: number;
}

/**
 * Pagination parameters for requests
 */
export interface PaginationParams {
    /** Page number (1-based) */
    page?: number;
    /** Items per page */
    per_page?: number;
    /** Maximum items per page allowed */
    max_per_page?: number;
}

/**
 * API Error response structure
 * Matches FastAPI error responses
 */
export interface ApiError {
    /** Error message */
    message: string;
    /** HTTP status code */
    status?: number;
    /** Error type/code */
    type?: string;
    /** Additional error details */
    details?: Record<string, unknown>;
    /** Field-specific validation errors */
    field_errors?: FieldError[];
}

/**
 * Field validation error
 */
export interface FieldError {
    /** Field name that has the error */
    field: string;
    /** Error message for the field */
    message: string;
    /** Error code/type */
    code?: string;
}

/**
 * Standard message response
 * Matches backend MessageResponse schema
 */
export interface MessageResponse {
    /** Response message */
    message: string;
}

/**
 * ISO 8601 date string
 * Used for all datetime fields from backend
 */
export type ISODateString = string;

/**
 * Request metadata that can be included in API calls
 */
export interface RequestMetadata {
    /** Request ID for tracing */
    request_id?: string;
    /** User agent information */
    user_agent?: string;
    /** Client version */
    client_version?: string;
}

/**
 * Type guard to check if a value is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
    return (
        typeof error === 'object' &&
        error !== null &&
        'message' in error &&
        typeof (error as any).message === 'string'
    );
}

/**
 * Type guard to check if a response is an ApiResponse
 */
export function isApiResponse<T>(response: unknown): response is ApiResponse<T> {
    return (
        typeof response === 'object' &&
        response !== null &&
        'data' in response &&
        (response as any).data !== undefined
    );
}

/**
 * Type guard to check if a response is paginated
 */
export function isPaginatedResponse<T>(response: unknown): response is PaginatedResponse<T> {
    return (
        typeof response === 'object' &&
        response !== null &&
        'items' in response &&
        'total' in response &&
        Array.isArray((response as any).items)
    );
}

/**
 * Extract data from ApiResponse, throwing on error
 */
export function extractApiData<T>(response: ApiResponse<T>): T {
    if (response.error) {
        throw new Error(response.error);
    }
    if (response.data === null) {
        throw new Error('API response data is null');
    }
    return response.data;
}

/**
 * Create a successful ApiResponse
 */
export function createApiResponse<T>(data: T): ApiResponse<T> {
    return { data };
}

/**
 * Create an error ApiResponse
 */
export function createApiErrorResponse<T = never>(error: string): ApiResponse<T> {
    return { data: null, error };
}

/**
 * Utility type for API endpoints that can accept FormData or JSON
 */
export type RequestBody = Record<string, unknown> | FormData;

/**
 * Common HTTP methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * API endpoint configuration
 */
export interface ApiEndpoint {
    /** HTTP method */
    method: HttpMethod;
    /** URL path */
    path: string;
    /** Whether authentication is required */
    requiresAuth?: boolean;
    /** Request timeout in milliseconds */
    timeout?: number;
}

/**
 * File upload progress information
 */
export interface UploadProgress {
    /** Bytes uploaded */
    loaded: number;
    /** Total bytes */
    total: number;
    /** Progress percentage (0-100) */
    percentage: number;
}

/**
 * Axios error with enhanced typing
 */
export interface TypedAxiosError extends Omit<AxiosError, 'response'> {
    response?: AxiosError['response'] & {
        data: ApiError;
    };
}

/**
 * Generic list response (when not paginated)
 */
export interface ListResponse<T> {
    /** Array of items */
    items: T[];
    /** Total count */
    total: number;
}

/**
 * Utility to build API URLs with proper formatting
 */
export function buildApiUrl(endpoint: string, params?: Record<string, string | number>): string {
    // Validate inputs
    if (!endpoint || typeof endpoint !== 'string') {
        throw new Error('endpoint must be a non-empty string');
    }

    // Ensure endpoint starts with slash and prepend /api
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    let url = `/api${cleanEndpoint}`;

    // Add query parameters if provided
    if (params && Object.keys(params).length > 0) {
        const searchParams = new URLSearchParams();
        for (const [key, value] of Object.entries(params)) {
            searchParams.append(key, String(value));
        }
        url += `?${searchParams.toString()}`;
    }

    return url;
}
