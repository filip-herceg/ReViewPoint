// Tests for authentication API types and utilities
import { describe, expect, it } from "vitest";
import {
	type AuthError,
	AuthErrorType,
	type AuthLoginRequest,
	type AuthTokens,
	DEFAULT_PASSWORD_REQUIREMENTS,
	decodeJWTPayload,
	EMAIL_REGEX,
	extractUserFromToken,
	isAuthError,
	isAuthTokens,
	isTokenExpired,
	type JWTPayload,
} from "@/lib/api/types/auth";
import { testLogger } from "../../../test-utils";

describe("AuthErrorType", () => {
	it("should have all expected error types", () => {
		testLogger.info("Testing AuthErrorType enum values");

		expect(AuthErrorType.INVALID_CREDENTIALS).toBe("invalid_credentials");
		expect(AuthErrorType.TOKEN_EXPIRED).toBe("token_expired");
		expect(AuthErrorType.TOKEN_INVALID).toBe("token_invalid");
		expect(AuthErrorType.USER_NOT_FOUND).toBe("user_not_found");
		expect(AuthErrorType.USER_ALREADY_EXISTS).toBe("user_already_exists");
		expect(AuthErrorType.PASSWORD_TOO_WEAK).toBe("password_too_weak");
		expect(AuthErrorType.EMAIL_INVALID).toBe("email_invalid");
		expect(AuthErrorType.RATE_LIMITED).toBe("rate_limited");
		expect(AuthErrorType.REFRESH_TOKEN_BLACKLISTED).toBe(
			"refresh_token_blacklisted",
		);
		expect(AuthErrorType.REFRESH_TOKEN_RATE_LIMITED).toBe(
			"refresh_token_rate_limited",
		);
		expect(AuthErrorType.SERVER_ERROR).toBe("server_error");
		expect(AuthErrorType.NETWORK_ERROR).toBe("network_error");
		expect(AuthErrorType.UNKNOWN).toBe("unknown");

		testLogger.debug("All AuthErrorType values are correct");
	});
});

describe("DEFAULT_PASSWORD_REQUIREMENTS", () => {
	it("should have expected default values", () => {
		testLogger.info("Testing default password requirements");

		expect(DEFAULT_PASSWORD_REQUIREMENTS.minLength).toBe(8);
		expect(DEFAULT_PASSWORD_REQUIREMENTS.maxLength).toBe(128);
		expect(DEFAULT_PASSWORD_REQUIREMENTS.requiresUppercase).toBe(false);
		expect(DEFAULT_PASSWORD_REQUIREMENTS.requiresLowercase).toBe(false);

		testLogger.debug("Default password requirements are correct");
	});
});

describe("EMAIL_REGEX", () => {
	it("should validate correct email formats", () => {
		testLogger.info("Testing email regex with valid emails");

		const validEmails = [
			"test@example.com",
			"user.name@domain.co.uk",
			"user+tag@example.org",
			"user123@test-domain.com",
		];

		validEmails.forEach((email) => {
			expect(EMAIL_REGEX.test(email)).toBe(true);
			testLogger.debug(`Valid email: ${email}`);
		});
	});

	it("should reject invalid email formats", () => {
		testLogger.info("Testing email regex with invalid emails");

		const invalidEmails = [
			"invalid",
			"@example.com",
			"user@",
			"user@domain",
			"",
		];

		invalidEmails.forEach((email) => {
			expect(EMAIL_REGEX.test(email)).toBe(false);
			testLogger.debug(`Invalid email: ${email}`);
		});
	});
});

describe("isAuthTokens", () => {
	it("should identify valid AuthTokens objects", () => {
		testLogger.info("Testing isAuthTokens type guard with valid objects");

		const validTokens: AuthTokens = {
			access_token: "access_token_value",
			refresh_token: "refresh_token_value",
			token_type: "bearer",
		};

		expect(isAuthTokens(validTokens)).toBe(true);
		testLogger.debug("Valid AuthTokens correctly identified");
	});

	it("should reject invalid objects", () => {
		testLogger.info("Testing isAuthTokens type guard with invalid objects");

		const invalidCases = [
			null,
			undefined,
			{},
			{ access_token: "token" }, // missing fields
			{ access_token: "token", refresh_token: "token", token_type: "basic" }, // wrong token_type
			{ access_token: 123, refresh_token: "token", token_type: "bearer" }, // wrong types
		];

		invalidCases.forEach((testCase) => {
			expect(isAuthTokens(testCase)).toBe(false);
		});

		testLogger.debug("Invalid objects correctly rejected");
	});
});

describe("isAuthError", () => {
	it("should identify valid AuthError objects", () => {
		testLogger.info("Testing isAuthError type guard with valid objects");

		const validError: AuthError = {
			type: AuthErrorType.INVALID_CREDENTIALS,
			message: "Invalid credentials provided",
			status: 401,
		};

		expect(isAuthError(validError)).toBe(true);
		testLogger.debug("Valid AuthError correctly identified");
	});

	it("should reject invalid objects", () => {
		testLogger.info("Testing isAuthError type guard with invalid objects");

		const invalidCases = [
			null,
			undefined,
			{},
			{ type: "unknown_type", message: "error" }, // invalid type
			{ message: "error" }, // missing type
			{ type: AuthErrorType.INVALID_CREDENTIALS }, // missing message
		];

		invalidCases.forEach((testCase) => {
			expect(isAuthError(testCase)).toBe(false);
		});

		testLogger.debug("Invalid objects correctly rejected");
	});
});

describe("JWT utilities", () => {
	// Create a mock JWT token for testing
	const mockPayload: JWTPayload = {
		sub: "user123",
		email: "test@example.com",
		exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
		iat: Math.floor(Date.now() / 1000),
		roles: ["user"],
	};

	const mockToken = [
		"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", // header
		btoa(JSON.stringify(mockPayload))
			.replace(/\+/g, "-")
			.replace(/\//g, "_")
			.replace(/=/g, ""), // payload
		"signature", // signature
	].join(".");

	const mockAuthTokens: AuthTokens = {
		access_token: mockToken,
		refresh_token: `refresh_${mockToken}`,
		token_type: "bearer",
	};

	describe("decodeJWTPayload", () => {
		it("should decode valid JWT token", () => {
			testLogger.info("Testing JWT payload decoding");

			const decoded = decodeJWTPayload(mockToken);

			expect(decoded).toBeTruthy();
			expect(decoded?.sub).toBe("user123");
			expect(decoded?.email).toBe("test@example.com");
			expect(decoded?.roles).toEqual(["user"]);

			testLogger.debug("JWT payload decoded correctly");
		});

		it("should return null for invalid tokens", () => {
			testLogger.info("Testing JWT decoding with invalid tokens");

			const invalidTokens = [
				"invalid.token",
				"invalid",
				"",
				"a.b", // too few parts
				"a.b.c.d", // too many parts
				"valid.invalidbase64.signature",
			];

			invalidTokens.forEach((token) => {
				expect(decodeJWTPayload(token)).toBeNull();
			});

			testLogger.debug("Invalid tokens correctly handled");
		});
	});

	describe("isTokenExpired", () => {
		it("should detect non-expired tokens", () => {
			testLogger.info("Testing token expiration with valid token");

			expect(isTokenExpired(mockPayload)).toBe(false);
			testLogger.debug("Non-expired token correctly identified");
		});

		it("should detect expired tokens", () => {
			testLogger.info("Testing token expiration with expired token");

			const expiredPayload = {
				...mockPayload,
				exp: Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
			};

			const _expiredToken = [
				"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
				btoa(JSON.stringify(expiredPayload))
					.replace(/\+/g, "-")
					.replace(/\//g, "_")
					.replace(/=/g, ""),
				"signature",
			].join(".");

			expect(isTokenExpired(expiredPayload)).toBe(true);
			testLogger.debug("Expired token correctly identified");
		});

		it("should treat invalid tokens as expired", () => {
			testLogger.info("Testing token expiration with invalid tokens");

			const invalidPayload = {} as JWTPayload; // Missing exp field
			expect(isTokenExpired(invalidPayload)).toBe(true);

			// Test with null payload
			expect(isTokenExpired(null as unknown as JWTPayload)).toBe(true);

			testLogger.debug("Invalid tokens treated as expired");
		});
	});

	describe("extractUserFromToken", () => {
		it("should extract user info from valid token", () => {
			testLogger.info("Testing user extraction from valid token");

			const user = extractUserFromToken(mockAuthTokens);

			expect(user).toBeTruthy();
			expect(user?.id).toBe("user123");
			expect(user?.email).toBe("test@example.com");
			expect(user?.roles).toEqual(["user"]);
			expect(user?.name).toBeUndefined(); // Not included in token by default

			testLogger.debug("User info extracted correctly from token");
		});

		it("should return null for invalid tokens", () => {
			testLogger.info("Testing user extraction from invalid tokens");

			const invalidTokens: AuthTokens = {
				access_token: "invalid",
				refresh_token: "invalid",
				token_type: "bearer",
			};
			expect(extractUserFromToken(invalidTokens)).toBeNull();

			const emptyTokens: AuthTokens = {
				access_token: "",
				refresh_token: "",
				token_type: "bearer",
			};
			expect(extractUserFromToken(emptyTokens)).toBeNull();

			// Token with missing required fields
			const incompletePayload = { sub: "user123" }; // missing email
			const incompleteToken = [
				"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
				btoa(JSON.stringify(incompletePayload))
					.replace(/\+/g, "-")
					.replace(/\//g, "_")
					.replace(/=/g, ""),
				"signature",
			].join(".");

			const incompleteTokens: AuthTokens = {
				access_token: incompleteToken,
				refresh_token: "refresh",
				token_type: "bearer",
			};
			expect(extractUserFromToken(incompleteTokens)).toBeNull();

			testLogger.debug("Invalid tokens correctly handled");
		});
	});
});

describe("Type validation integration", () => {
	it("should validate complete auth flow types", () => {
		testLogger.info("Testing complete auth flow type validation");

		// Login request
		const loginRequest: AuthLoginRequest = {
			email: "test@example.com",
			password: "securepassword123",
		};

		expect(loginRequest.email).toBe("test@example.com");

		// Auth tokens response
		const tokens: AuthTokens = {
			access_token: "access_token_here",
			refresh_token: "refresh_token_here",
			token_type: "bearer",
		};

		expect(isAuthTokens(tokens)).toBe(true);

		testLogger.debug("Complete auth flow types validated successfully");
	});

	it("should handle auth errors properly", () => {
		testLogger.info("Testing auth error handling");

		const authError: AuthError = {
			type: AuthErrorType.INVALID_CREDENTIALS,
			message: "The provided credentials are invalid",
			status: 401,
			details: {
				attempt_count: 3,
				lockout_time: "2025-01-01T00:00:00Z",
			},
		};

		expect(isAuthError(authError)).toBe(true);
		expect(authError.details?.attempt_count).toBe(3);

		testLogger.debug("Auth error handling validated successfully");
	});
});
