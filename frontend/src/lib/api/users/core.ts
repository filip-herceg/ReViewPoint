/**
 * Users Core API Module
 *
 * Provides core user management functionality for the ReViewPoint application.
 * This module mirrors the backend user core endpoints and provides a consistent
 * interface for user CRUD operations, search, and management.
 *
 * ## Endpoints
 * - `POST /users` - Create a new user (admin only)
 * - `GET /users` - List users with filtering and pagination
 * - `GET /users/{user_id}` - Get specific user by ID
 * - `PUT /users/{user_id}` - Update user information
 * - `DELETE /users/{user_id}` - Delete user (admin only)
 * - `GET /users/search` - Search users with advanced filters
 *
 * ## Usage
 *
 * ### User Creation (Admin Only)
 * ```typescript
 * import { usersCoreApi } from '@/lib/api';
 *
 * const userData = {
 *   email: 'newuser@example.com',
 *   name: 'New User',
 *   password: 'securepassword123'
 * };
 *
 * try {
 *   const user = await usersCoreApi.createUser(userData);
 *   console.log('User created:', user);
 * } catch (error) {
 *   console.error('User creation failed:', error.message);
 * }
 * ```
 *
 * ### User Listing with Pagination
 * ```typescript
 * try {
 *   const response = await usersCoreApi.listUsers({
 *     limit: 20,
 *     offset: 0,
 *     email: 'search@example.com',
 *     name: 'John',
 *     created_after: '2024-01-01T00:00:00Z'
 *   });
 *
 *   console.log('Users:', response.users);
 *   console.log('Total count:', response.total);
 * } catch (error) {
 *   console.error('Failed to list users:', error.message);
 * }
 * ```
 *
 * ### Get User by ID
 * ```typescript
 * try {
 *   const user = await usersCoreApi.getUser(123);
 *   console.log('User details:', user);
 * } catch (error) {
 *   console.error('User not found:', error.message);
 * }
 * ```
 *
 * ### Update User
 * ```typescript
 * const updateData = {
 *   name: 'Updated Name',
 *   email: 'updated@example.com'
 * };
 *
 * try {
 *   const updatedUser = await usersCoreApi.updateUser(123, updateData);
 *   console.log('User updated:', updatedUser);
 * } catch (error) {
 *   console.error('Update failed:', error.message);
 * }
 * ```
 *
 * ### Delete User (Admin Only)
 * ```typescript
 * try {
 *   await usersCoreApi.deleteUser(123);
 *   console.log('User deleted successfully');
 * } catch (error) {
 *   console.error('Delete failed:', error.message);
 * }
 * ```
 *
 * ## Search and Filtering
 * The `listUsers` function supports various filtering options:
 * - `offset`: Number of users to skip (pagination)
 * - `limit`: Maximum number of users to return
 * - `email`: Filter by email address (exact match)
 * - `name`: Filter by name (partial match)
 * - `created_after`: Filter by creation date (ISO string)
 *
 * ## User Data Structure
 * Users have the following properties:
 * - `id`: Unique user identifier
 * - `email`: User's email address
 * - `name`: User's display name
 * - `bio`: User's biography (optional)
 * - `avatar_url`: URL to user's avatar image (optional)
 * - `created_at`: User creation timestamp
 * - `updated_at`: Last update timestamp
 *
 * ## Error Handling
 * User functions throw errors for:
 * - Invalid user data
 * - Permission denied
 * - User not found
 * - Email already exists
 * - Network errors
 *
 * ## Security Features
 * - Admin-only endpoints for user creation and deletion
 * - Data validation
 * - User authentication required
 * - Role-based access control
 *
 * @see backend/src/api/v1/users/core.py for corresponding backend implementation
 */

// User CRUD API functions
// Mirrors backend/src/api/v1/users/core.py

import logger from "@/logger";
import { request } from "../base";

// Types that match the backend
interface UserCreateRequest {
	email: string;
	name: string;
	password: string;
}

interface User {
	id: number;
	email: string;
	name: string;
	bio?: string;
	avatar_url?: string;
	created_at?: string;
	updated_at?: string;
}

interface UserListResponse {
	users: User[];
	total: number;
}

interface UserSearchParams {
	offset?: number;
	limit?: number;
	email?: string;
	name?: string;
	created_after?: string;
}

export const usersCoreApi = {
	// Create a new user (admin only)
	createUser: async (userData: UserCreateRequest): Promise<User> => {
		logger.info("Creating user", { email: userData.email });
		const response = await request<User>("/users", {
			method: "POST",
			data: userData,
		});

		if (response.error) {
			logger.warn("User creation failed", {
				error: response.error,
				email: userData.email,
			});
			throw new Error(response.error);
		}

		logger.info("User created successfully", {
			id: response.data?.id,
			email: response.data?.email,
		});
		return response.data!;
	},

	// List users with optional filtering (admin only)
	listUsers: async (params?: UserSearchParams): Promise<UserListResponse> => {
		logger.info("Fetching users list", { params });
		const queryParams = params
			? new URLSearchParams(params as any).toString()
			: "";
		const url = queryParams ? `/users?${queryParams}` : "/users";

		const response = await request<UserListResponse>(url);

		if (response.error) {
			logger.warn("Failed to fetch users", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Users fetched successfully", {
			total: response.data?.total,
			count: response.data?.users.length,
		});
		return response.data!;
	},

	// Get user by ID (admin only)
	getUserById: async (userId: number): Promise<User> => {
		logger.info("Fetching user by ID", { userId });
		const response = await request<User>(`/users/${userId}`);

		if (response.error) {
			logger.warn("Failed to fetch user", { error: response.error, userId });
			throw new Error(response.error);
		}

		logger.info("User fetched successfully", {
			id: response.data?.id,
			email: response.data?.email,
		});
		return response.data!;
	},

	// Update user information (admin only)
	updateUser: async (
		userId: number,
		userData: UserCreateRequest,
	): Promise<User> => {
		logger.info("Updating user", { userId, email: userData.email });
		const response = await request<User>(`/users/${userId}`, {
			method: "PUT",
			data: userData,
		});

		if (response.error) {
			logger.warn("User update failed", { error: response.error, userId });
			throw new Error(response.error);
		}

		logger.info("User updated successfully", {
			id: response.data?.id,
			email: response.data?.email,
		});
		return response.data!;
	},

	// Delete user (admin only)
	deleteUser: async (userId: number): Promise<void> => {
		logger.info("Deleting user", { userId });
		const response = await request<null>(`/users/${userId}`, {
			method: "DELETE",
		});

		if (response.error) {
			logger.warn("User deletion failed", { error: response.error, userId });
			throw new Error(response.error);
		}

		logger.info("User deleted successfully", { userId });
	},
};
