// Authentication API functions
// Mirrors backend/src/api/v1/auth.py

import logger from "@/logger";
import { request } from "./base";

// Types that match the backend
interface UserRegisterRequest {
	email: string;
	password: string;
	name: string;
}

interface UserLoginRequest {
	email: string;
	password: string;
}

interface AuthResponse {
	access_token: string;
	refresh_token: string;
}

interface MessageResponse {
	message: string;
}

interface PasswordResetRequest {
	email: string;
}

interface PasswordResetConfirmRequest {
	token: string;
	new_password: string;
}

interface UserProfile {
	id: number;
	email: string;
	name: string;
	bio?: string;
	avatar_url?: string;
	created_at?: string;
	updated_at?: string;
}

interface RefreshTokenRequest {
	refresh_token: string;
}

export const authApi = {
	// Register a new user
	register: async (userData: UserRegisterRequest): Promise<AuthResponse> => {
		logger.info("Registering user", { email: userData.email });
		const response = await request<AuthResponse>("/auth/register", {
			method: "POST",
			data: userData,
		});

		if (response.error) {
			logger.warn("User registration failed", {
				error: response.error,
				email: userData.email,
			});
			throw new Error(response.error);
		}

		logger.info("User registered successfully", { email: userData.email });
		return response.data!;
	},

	// User login
	login: async (loginData: UserLoginRequest): Promise<AuthResponse> => {
		logger.info("User login attempt", { email: loginData.email });
		const response = await request<AuthResponse>("/auth/login", {
			method: "POST",
			data: loginData,
		});

		if (response.error) {
			logger.warn("User login failed", {
				error: response.error,
				email: loginData.email,
			});
			throw new Error(response.error);
		}

		logger.info("User logged in successfully", { email: loginData.email });
		return response.data!;
	},

	// User logout
	logout: async (): Promise<MessageResponse> => {
		logger.info("User logout attempt");
		const response = await request<MessageResponse>("/auth/logout", {
			method: "POST",
		});

		if (response.error) {
			logger.warn("User logout failed", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("User logged out successfully");
		return response.data!;
	},

	// Refresh JWT access token
	refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
		logger.info("Refreshing access token");
		const response = await request<AuthResponse>("/auth/refresh-token", {
			method: "POST",
			data: { refresh_token: refreshToken },
		});

		if (response.error) {
			logger.warn("Token refresh failed", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Token refreshed successfully");
		return response.data!;
	},

	// Request password reset
	requestPasswordReset: async (email: string): Promise<MessageResponse> => {
		logger.info("Requesting password reset", { email });
		const response = await request<MessageResponse>(
			"/auth/request-password-reset",
			{
				method: "POST",
				data: { email },
			},
		);

		if (response.error) {
			logger.warn("Password reset request failed", {
				error: response.error,
				email,
			});
			throw new Error(response.error);
		}

		logger.info("Password reset requested successfully", { email });
		return response.data!;
	},

	// Reset password with token
	resetPassword: async (
		token: string,
		newPassword: string,
	): Promise<MessageResponse> => {
		logger.info("Resetting password with token");
		const response = await request<MessageResponse>("/auth/reset-password", {
			method: "POST",
			data: { token, new_password: newPassword },
		});

		if (response.error) {
			logger.warn("Password reset failed", { error: response.error });
			throw new Error(response.error);
		}

		logger.info("Password reset successfully");
		return response.data!;
	},

	// Get current user profile
	getCurrentUser: async (): Promise<UserProfile> => {
		logger.info("Getting current user profile");
		const response = await request<UserProfile>("/auth/me");

		if (response.error) {
			logger.warn("Failed to get current user profile", {
				error: response.error,
			});
			throw new Error(response.error);
		}

		logger.info("Current user profile retrieved successfully");
		return response.data!;
	},
};
