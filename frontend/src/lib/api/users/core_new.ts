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
