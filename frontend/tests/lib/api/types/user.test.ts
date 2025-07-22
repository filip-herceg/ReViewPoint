import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
	DEFAULT_USER_PREFERENCES,
	formatUserCreatedAt,
	getUserDisplayName,
	getUserInitials,
	isUser,
	isUserAdmin,
	isUserPreferences,
	isUserRole,
	type User,
	type UserActivity,
	type UserCreateRequest,
	type UserInvitation,
	type UserListResponse,
	type UserPreferences,
	type UserPreferencesUpdateRequest,
	UserRole,
	type UserSearchParams,
	type UserTheme,
	type UserUpdateRequest,
	type UserWithRoles,
	userHasRole,
} from "@/lib/api/types/user";
import logger from "@/logger";

// Helper function to create test users
function createTestUser(overrides: Partial<User> = {}): User {
	return {
		id: 123,
		email: "test@example.com",
		name: "Test User",
		bio: "Test bio",
		avatar_url: null,
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString(),
		...overrides,
	};
}

// Helper function to create test user with roles
function createTestUserWithRoles(
	overrides: Partial<UserWithRoles> = {},
): UserWithRoles {
	return {
		...createTestUser(),
		roles: [UserRole.USER],
		permissions: [],
		...overrides,
	};
}

describe("User Types", () => {
	beforeEach(() => {
		logger.info("Starting user types test");
	});

	afterEach(() => {
		logger.info("Completed user types test");
	});

	describe("Type Guards", () => {
		describe("isUser", () => {
			it("should return true for valid user objects", () => {
				const user = createTestUser();
				expect(isUser(user)).toBe(true);
			});

			it("should return false for invalid user objects", () => {
				expect(isUser(null)).toBe(false);
				expect(isUser(undefined)).toBe(false);
				expect(isUser({})).toBe(false);
				expect(isUser({ id: "test" })).toBe(false);
				expect(isUser({ id: 123 })).toBe(false);
				expect(isUser({ id: 123, email: "test@test.com" })).toBe(true);
			});

			it("should validate required user fields", () => {
				const baseUser = createTestUser();

				// Test missing id
				const userWithoutId = { ...baseUser } as any;
				delete userWithoutId.id;
				expect(isUser(userWithoutId)).toBe(false);

				// Test missing email
				const userWithoutEmail = { ...baseUser } as any;
				delete userWithoutEmail.email;
				expect(isUser(userWithoutEmail)).toBe(false);

				// Test invalid id type
				const userWithStringId = { ...baseUser, id: "string-id" };
				expect(isUser(userWithStringId)).toBe(false);

				// Test invalid email type
				const userWithNumberEmail = { ...baseUser, email: 123 };
				expect(isUser(userWithNumberEmail)).toBe(false);
			});
		});

		describe("isUserPreferences", () => {
			it("should return true for valid user preferences objects", () => {
				const preferences: UserPreferences = {
					theme: "dark",
					locale: "en",
				};
				expect(isUserPreferences(preferences)).toBe(true);
			});

			it("should return false for invalid user preferences objects", () => {
				expect(isUserPreferences(null)).toBe(false);
				expect(isUserPreferences(undefined)).toBe(false);
				expect(isUserPreferences({ theme: "invalid" })).toBe(false);
			});

			it("should validate theme values", () => {
				expect(isUserPreferences({ theme: "dark" })).toBe(true);
				expect(isUserPreferences({ theme: "light" })).toBe(true);
				expect(isUserPreferences({ theme: "blue" })).toBe(false);
			});

			it("should allow empty preferences", () => {
				expect(isUserPreferences({})).toBe(true);
			});
		});

		describe("isUserRole", () => {
			it("should return true for valid user roles", () => {
				expect(isUserRole(UserRole.ADMIN)).toBe(true);
				expect(isUserRole(UserRole.MODERATOR)).toBe(true);
				expect(isUserRole(UserRole.USER)).toBe(true);
				expect(isUserRole(UserRole.GUEST)).toBe(true);
			});

			it("should return false for invalid user roles", () => {
				expect(isUserRole("invalid")).toBe(false);
				expect(isUserRole(null)).toBe(false);
				expect(isUserRole(undefined)).toBe(false);
				expect(isUserRole(123)).toBe(false);
			});
		});
	});

	describe("Helper Functions", () => {
		describe("getUserDisplayName", () => {
			it("should return name when available", () => {
				const user = createTestUser({ name: "Test User" });
				expect(getUserDisplayName(user)).toBe("Test User");
			});

			it("should return email username when name is not available", () => {
				const user = createTestUser({ name: null, email: "test@example.com" });
				expect(getUserDisplayName(user)).toBe("test");
			});

			it("should handle email-only users correctly", () => {
				const user = { email: "john.doe@example.com", name: null };
				expect(getUserDisplayName(user)).toBe("john.doe");
			});
		});

		describe("getUserInitials", () => {
			it("should generate initials from name", () => {
				const user = createTestUser({ name: "John Doe" });
				expect(getUserInitials(user)).toBe("JD");
			});

			it("should generate initials from email when name is not available", () => {
				const user = createTestUser({
					name: null,
					email: "john.doe@example.com",
				});
				expect(getUserInitials(user)).toBe("JO");
			});

			it("should handle single names correctly", () => {
				const user = createTestUser({ name: "John" });
				expect(getUserInitials(user)).toBe("JO");
			});

			it("should handle multiple names correctly", () => {
				const user = createTestUser({ name: "John Michael Doe" });
				expect(getUserInitials(user)).toBe("JD");
			});
		});

		describe("userHasRole", () => {
			it("should return true when user has the specified role", () => {
				const user = createTestUserWithRoles({
					roles: [UserRole.ADMIN, UserRole.USER],
				});
				expect(userHasRole(user, UserRole.ADMIN)).toBe(true);
				expect(userHasRole(user, UserRole.USER)).toBe(true);
			});

			it("should return false when user does not have the specified role", () => {
				const user = createTestUserWithRoles({
					roles: [UserRole.USER],
				});
				expect(userHasRole(user, UserRole.ADMIN)).toBe(false);
				expect(userHasRole(user, UserRole.MODERATOR)).toBe(false);
			});
		});

		describe("isUserAdmin", () => {
			it("should return true for admin users", () => {
				const user = createTestUserWithRoles({
					roles: [UserRole.ADMIN],
				});
				expect(isUserAdmin(user)).toBe(true);
			});

			it("should return false for non-admin users", () => {
				const user = createTestUserWithRoles({
					roles: [UserRole.USER],
				});
				expect(isUserAdmin(user)).toBe(false);
			});
		});

		describe("formatUserCreatedAt", () => {
			it("should format valid creation date", () => {
				const user = createTestUser({ created_at: "2023-01-01T00:00:00Z" });
				const formatted = formatUserCreatedAt(user);
				// Allow for different locale formats (e.g., "1/1/2023" or "1.1.2023")
				expect(formatted).toMatch(/\d{1,2}[./]\d{1,2}[./]\d{4}/);
			});

			it('should return "Unknown" for null creation date', () => {
				const user = createTestUser({ created_at: null });
				expect(formatUserCreatedAt(user)).toBe("Unknown");
			});
		});
	});

	describe("Default Values", () => {
		describe("DEFAULT_USER_PREFERENCES", () => {
			it("should have correct default values", () => {
				expect(DEFAULT_USER_PREFERENCES.theme).toBe("light");
				expect(DEFAULT_USER_PREFERENCES.locale).toBe("en");
			});
		});
	});

	describe("Enums", () => {
		describe("UserRole", () => {
			it("should contain all expected roles", () => {
				expect(UserRole.ADMIN).toBe("admin");
				expect(UserRole.MODERATOR).toBe("moderator");
				expect(UserRole.USER).toBe("user");
				expect(UserRole.GUEST).toBe("guest");
			});
		});

		describe("UserTheme", () => {
			it("should be a valid union type", () => {
				const darkTheme: UserTheme = "dark";
				const lightTheme: UserTheme = "light";

				expect(darkTheme).toBe("dark");
				expect(lightTheme).toBe("light");
			});
		});
	});

	describe("Complex Type Tests", () => {
		describe("UserListResponse", () => {
			it("should structure user list response correctly", () => {
				const response: UserListResponse = {
					users: [createTestUser(), createTestUser()],
					total: 2,
				};

				expect(response.users).toHaveLength(2);
				expect(response.total).toBe(2);
				expect(response.users[0]).toSatisfy(isUser);
				expect(response.users[1]).toSatisfy(isUser);
			});
		});

		describe("UserActivity", () => {
			it("should structure user activity correctly", () => {
				const activity: UserActivity = {
					id: "activity-1",
					user_id: 123,
					type: "login",
					description: "User logged in",
					timestamp: new Date().toISOString(),
					ip_address: "127.0.0.1",
					user_agent: "Test Agent",
					metadata: { session_id: "test-session" },
				};

				expect(activity.id).toBe("activity-1");
				expect(activity.user_id).toBe(123);
				expect(activity.type).toBe("login");
				expect(activity.description).toBe("User logged in");
				expect(typeof activity.timestamp).toBe("string");
			});
		});

		describe("UserSearchParams", () => {
			it("should structure search parameters correctly", () => {
				const searchParams: UserSearchParams = {
					query: "john",
					theme: "dark",
					locale: "en",
					sort_by: "created_at",
					sort_order: "desc",
				};

				expect(searchParams.query).toBe("john");
				expect(searchParams.theme).toBe("dark");
				expect(searchParams.locale).toBe("en");
				expect(searchParams.sort_by).toBe("created_at");
				expect(searchParams.sort_order).toBe("desc");
			});
		});

		describe("UserInvitation", () => {
			it("should structure user invitation correctly", () => {
				const invitation: UserInvitation = {
					id: "inv-1",
					email: "newuser@example.com",
					token: "invite-token",
					invited_by: 123,
					created_at: new Date().toISOString(),
					expires_at: new Date(
						Date.now() + 7 * 24 * 60 * 60 * 1000,
					).toISOString(),
					is_accepted: false,
				};

				expect(invitation.id).toBe("inv-1");
				expect(invitation.email).toBe("newuser@example.com");
				expect(invitation.token).toBe("invite-token");
				expect(invitation.invited_by).toBe(123);
				expect(invitation.is_accepted).toBe(false);
			});
		});

		describe("UserCreateRequest", () => {
			it("should structure user creation request correctly", () => {
				const request: UserCreateRequest = {
					email: "new@example.com",
					password: "SecurePass123!",
					name: "New User",
				};

				expect(request.email).toBe("new@example.com");
				expect(request.password).toBe("SecurePass123!");
				expect(request.name).toBe("New User");
			});
		});

		describe("UserUpdateRequest", () => {
			it("should structure user update request correctly", () => {
				const request: UserUpdateRequest = {
					name: "Updated Name",
					bio: "Updated bio",
				};

				expect(request.name).toBe("Updated Name");
				expect(request.bio).toBe("Updated bio");
			});
		});

		describe("UserPreferencesUpdateRequest", () => {
			it("should structure preferences update request correctly", () => {
				const request: UserPreferencesUpdateRequest = {
					preferences: {
						theme: "dark",
						locale: "fr",
						notifications: true,
					},
				};

				expect(request.preferences.theme).toBe("dark");
				expect(request.preferences.locale).toBe("fr");
				expect(request.preferences.notifications).toBe(true);
			});
		});
	});
});
