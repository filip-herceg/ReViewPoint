// User management types
// Maps to backend/src/schemas/user.py

import type { ISODateString, PaginatedResponse } from "./common";

/**
 * User theme preference
 */
export type UserTheme = "dark" | "light";

/**
 * Complete user profile
 * Matches backend UserProfile schema
 */
export interface User {
	/** User ID */
	id: number;
	/** User email address */
	email: string;
	/** User display name */
	name: string | null;
	/** User bio/description */
	bio: string | null;
	/** Avatar image URL */
	avatar_url: string | null;
	/** Account creation timestamp */
	created_at: ISODateString | null;
	/** Last update timestamp */
	updated_at: ISODateString | null;
}

/**
 * User profile update request
 * Matches backend UserProfileUpdate schema
 */
export interface UserUpdateRequest {
	/** Updated display name (max 128 chars) */
	name?: string | null;
	/** Updated bio (max 512 chars) */
	bio?: string | null;
}

/**
 * User preferences
 * Matches backend UserPreferences schema
 */
export interface UserPreferences {
	/** UI theme preference */
	theme?: UserTheme | null;
	/** User locale (e.g., 'en', 'fr') */
	locale?: string | null;
	// Additional preference fields can be added here
}

/**
 * User preferences update request
 * Matches backend UserPreferencesUpdate schema
 */
export interface UserPreferencesUpdateRequest {
	/** Preferences object with arbitrary key-value pairs */
	preferences: Record<string, unknown>;
}

/**
 * User avatar response
 * Matches backend UserAvatarResponse schema
 */
export interface UserAvatarResponse {
	/** Avatar image URL */
	avatar_url: string;
}

/**
 * User creation request
 * Matches backend UserCreateRequest schema
 */
export interface UserCreateRequest {
	/** User email address */
	email: string;
	/** User password */
	password: string;
	/** User display name */
	name: string;
}

/**
 * User read response
 * Matches backend UserRead schema (alias of UserProfile)
 */
export type UserResponse = User;

/**
 * User list response
 * Matches backend UserListResponse schema
 */
export interface UserListResponse {
	/** Array of users */
	users: User[];
	/** Total number of users */
	total: number;
}

/**
 * Paginated user list response
 */
export type PaginatedUserListResponse = PaginatedResponse<User>;

/**
 * User search/filter parameters
 */
export interface UserSearchParams {
	/** Search query (name, email) */
	query?: string;
	/** Filter by theme preference */
	theme?: UserTheme;
	/** Filter by locale */
	locale?: string;
	/** Sort field */
	sort_by?: "name" | "email" | "created_at" | "updated_at";
	/** Sort direction */
	sort_order?: "asc" | "desc";
}

/**
 * User statistics/summary
 */
export interface UserStats {
	/** Total number of users */
	total_users: number;
	/** Number of active users (last 30 days) */
	active_users: number;
	/** Number of new users (last 7 days) */
	new_users: number;
	/** User growth percentage */
	growth_percentage: number;
}

/**
 * User activity record
 */
export interface UserActivity {
	/** Activity ID */
	id: string;
	/** User ID */
	user_id: number;
	/** Activity type */
	type: "login" | "logout" | "profile_update" | "upload" | "download";
	/** Activity description */
	description: string;
	/** Activity timestamp */
	timestamp: ISODateString;
	/** IP address */
	ip_address?: string;
	/** User agent */
	user_agent?: string;
	/** Additional metadata */
	metadata?: Record<string, unknown>;
}

/**
 * User session information
 */
export interface UserSession {
	/** Session ID */
	id: string;
	/** User ID */
	user_id: number;
	/** Session start time */
	started_at: ISODateString;
	/** Last activity time */
	last_activity: ISODateString;
	/** IP address */
	ip_address: string;
	/** User agent */
	user_agent: string;
	/** Whether session is active */
	is_active: boolean;
}

/**
 * User role/permission types
 */
export enum UserRole {
	ADMIN = "admin",
	MODERATOR = "moderator",
	USER = "user",
	GUEST = "guest",
}

/**
 * User with roles (extended profile)
 */
export interface UserWithRoles extends User {
	/** User roles */
	roles: UserRole[];
	/** User permissions */
	permissions: string[];
}

/**
 * User invitation
 */
export interface UserInvitation {
	/** Invitation ID */
	id: string;
	/** Invited email */
	email: string;
	/** Invitation token */
	token: string;
	/** Inviter user ID */
	invited_by: number;
	/** Invitation creation time */
	created_at: ISODateString;
	/** Invitation expiry time */
	expires_at: ISODateString;
	/** Whether invitation is accepted */
	is_accepted: boolean;
	/** Acceptance timestamp */
	accepted_at?: ISODateString;
}

/**
 * User invitation request
 */
export interface UserInvitationRequest {
	/** Email to invite */
	email: string;
	/** Optional message */
	message?: string;
	/** Assigned roles */
	roles?: UserRole[];
}

/**
 * Type guard for User
 */
export function isUser(value: unknown): value is User {
	return (
		typeof value === "object" &&
		value !== null &&
		"id" in value &&
		"email" in value &&
		typeof (value as Record<string, unknown>).id === "number" &&
		typeof (value as Record<string, unknown>).email === "string"
	);
}

/**
 * Type guard for UserPreferences
 */
export function isUserPreferences(value: unknown): value is UserPreferences {
	return (
		typeof value === "object" &&
		value !== null &&
		(!("theme" in value) ||
			(typeof (value as Record<string, unknown>).theme === "string" &&
				["dark", "light"].includes(
					(value as Record<string, unknown>).theme as string,
				))) &&
		(!("locale" in value) ||
			typeof (value as Record<string, unknown>).locale === "string")
	);
}

/**
 * Type guard for UserRole
 */
export function isUserRole(value: unknown): value is UserRole {
	return (
		typeof value === "string" &&
		Object.values(UserRole).includes(value as UserRole)
	);
}

/**
 * Default user preferences
 */
export const DEFAULT_USER_PREFERENCES: UserPreferences = {
	theme: "light",
	locale: "en",
};

/**
 * Utility to create a display name for a user
 */
export function getUserDisplayName(user: Pick<User, "name" | "email">): string {
	return user.name || user.email.split("@")[0];
}

/**
 * Utility to get user initials for avatar
 */
export function getUserInitials(user: Pick<User, "name" | "email">): string {
	const displayName = getUserDisplayName(user);
	const parts = displayName.trim().split(/\s+/);

	if (parts.length === 1) {
		return parts[0].substring(0, 2).toUpperCase();
	}

	return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Utility to check if user has a specific role
 */
export function userHasRole(user: UserWithRoles, role: UserRole): boolean {
	return user.roles.includes(role);
}

/**
 * Utility to check if user has admin privileges
 */
export function isUserAdmin(user: UserWithRoles): boolean {
	return userHasRole(user, UserRole.ADMIN);
}

/**
 * Utility to format user creation date
 */
export function formatUserCreatedAt(user: User): string {
	if (!user.created_at) {
		return "Unknown";
	}

	return new Date(user.created_at).toLocaleDateString();
}
