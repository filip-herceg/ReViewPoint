// Central export point for all API types
// Import and re-export all type definitions for easy consumption

import type { AuthError, AuthLoginRequest, AuthRegisterRequest } from "./auth";
// Import types first for use in utility types
import type {
	ApiError,
	ApiResponse,
	ISODateString,
	ListResponse,
	PaginatedResponse,
	PaginationParams,
} from "./common";
import type { FileUploadConfig, UploadError } from "./upload";
import type { UserCreateRequest, UserUpdateRequest } from "./user";

// Authentication types
export type {
	AuthError,
	AuthLoginRequest,
	AuthLoginResponse,
	AuthLogoutResponse,
	AuthPasswordResetConfirmRequest,
	AuthPasswordResetConfirmResponse,
	AuthPasswordResetRequest,
	AuthPasswordResetResponse,
	AuthRegisterRequest,
	AuthRegisterResponse,
	AuthState,
	AuthTokenRefreshResponse,
	AuthTokens,
	AuthUser,
	JWTPayload,
	PasswordRequirements,
	TokenType,
} from "./auth";
export {
	AuthErrorType,
	DEFAULT_PASSWORD_REQUIREMENTS,
	decodeJWTPayload,
	EMAIL_REGEX,
	extractUserFromToken,
	isAuthError,
	isAuthTokens,
	isTokenExpired,
} from "./auth";
// Common types
export type {
	ApiEndpoint,
	ApiError,
	ApiResponse,
	FieldError,
	HttpMethod,
	ISODateString,
	ListResponse,
	MessageResponse,
	PaginatedResponse,
	PaginationParams,
	RequestBody,
	RequestMetadata,
	TypedAxiosError,
	UploadProgress,
} from "./common";
export {
	buildApiUrl,
	createApiErrorResponse,
	createApiResponse,
	extractApiData,
	HttpStatusCode,
	isApiError,
	isApiResponse,
	isPaginatedResponse,
} from "./common";

// Upload types
export type {
	BulkFileOperation,
	File,
	FileActionResult,
	FileDeleteRequest,
	FileDownloadRequest,
	FileListItem,
	FileListResponse,
	FileManagementConfig,
	FileManagementState,
	FilePreviewConfig,
	FileSearchParams,
	FileSharing,
	FileUpdateEvent,
	FileUploadConfig,
	FileUploadResponse,
	PaginatedFileListResponse,
	Upload,
	UploadCreateRequest,
	UploadError,
	UploadStatus,
} from "./upload";

export {
	calculateUploadProgress,
	formatUploadSize,
	isUpload,
	isUploadCompleted,
	isUploadError,
	isUploadFailed,
	isUploadInProgress,
	UploadErrorType,
	validateUploadStatus,
} from "./upload";

// User types
export type {
	PaginatedUserListResponse,
	User,
	UserActivity,
	UserAvatarResponse,
	UserCreateRequest,
	UserInvitation,
	UserInvitationRequest,
	UserListResponse,
	UserPreferences,
	UserPreferencesUpdateRequest,
	UserResponse,
	UserSearchParams,
	UserSession,
	UserStats,
	UserTheme,
	UserUpdateRequest,
	UserWithRoles,
} from "./user";

export {
	DEFAULT_USER_PREFERENCES,
	formatUserCreatedAt,
	getUserDisplayName,
	getUserInitials,
	isUser,
	isUserAdmin,
	isUserPreferences,
	isUserRole,
	UserRole,
	userHasRole,
} from "./user";

// Type utilities
/**
 * Extract the data type from an ApiResponse
 */
export type ExtractApiData<T> = T extends ApiResponse<infer U> ? U : never;

/**
 * Extract the item type from a paginated response
 */
export type ExtractPaginatedItem<T> =
	T extends PaginatedResponse<infer U> ? U : never;

/**
 * Extract the item type from a list response
 */
export type ExtractListItem<T> = T extends ListResponse<infer U> ? U : never;

/**
 * Make all properties of T optional recursively
 */
export type DeepPartial<T> = {
	[P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Make specific properties of T required
 */
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * Exclude specific properties from T
 */
export type OmitFields<T, K extends keyof T> = Omit<T, K>;

/**
 * Pick specific properties from T and make them required
 */
export type PickRequired<T, K extends keyof T> = Required<Pick<T, K>>;

/**
 * Create a type that represents the keys of T that are optional
 */
export type OptionalKeys<T> = {
	[K in keyof T]-?: Record<string, never> extends Pick<T, K> ? K : never;
}[keyof T];

/**
 * Create a type that represents the keys of T that are required
 */
export type RequiredKeys<T> = {
	[K in keyof T]-?: Record<string, never> extends Pick<T, K> ? never : K;
}[keyof T];

/**
 * Create a union type of all possible API error types
 */
export type AnyApiError = ApiError | AuthError | UploadError;

/**
 * Create a union type of all possible response types
 */
export type AnyApiResponse<T = unknown> = ApiResponse<T>;

/**
 * Helper type for form data that can be sent to API
 */
export type ApiFormData =
	| AuthRegisterRequest
	| AuthLoginRequest
	| UserUpdateRequest
	| UserCreateRequest
	| FileUploadConfig;

/**
 * Helper type for API responses that include data
 */
export type DataApiResponse<T> = ApiResponse<T> & { data: T };

/**
 * Helper type for API responses that include errors
 */
export type ErrorApiResponse = ApiResponse<never> & { error: string };

/**
 * Type for API endpoint handlers
 */
export type ApiHandler<TRequest = unknown, TResponse = unknown> = (
	request: TRequest,
) => Promise<ApiResponse<TResponse>>;

/**
 * Type for paginated API endpoint handlers
 */
export type PaginatedApiHandler<TItem, TParams = unknown> = (
	params: TParams & PaginationParams,
) => Promise<ApiResponse<PaginatedResponse<TItem>>>;

/**
 * Common API status types
 */
export type ApiStatus = "idle" | "loading" | "success" | "error";

/**
 * Generic API state for stores
 */
export interface ApiState<T> {
	data: T | null;
	status: ApiStatus;
	error: string | null;
	lastUpdated: ISODateString | null;
}

/**
 * Create default API state
 */
export function createDefaultApiState<T>(): ApiState<T> {
	return {
		data: null,
		status: "idle",
		error: null,
		lastUpdated: null,
	};
}

/**
 * Type guard for API state in loading
 */
export function isApiStateLoading<T>(state: ApiState<T>): boolean {
	return state.status === "loading";
}

/**
 * Type guard for API state in error
 */
export function isApiStateError<T>(state: ApiState<T>): boolean {
	return state.status === "error";
}

/**
 * Type guard for API state with success data
 */
export function isApiStateSuccess<T>(
	state: ApiState<T>,
): state is ApiState<T> & { data: T } {
	return state.status === "success" && state.data !== null;
}
