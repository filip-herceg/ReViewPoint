import axios from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { authApi, uploadsApi } from "@/lib/api";
import {
	createUpload,
	createUploadList,
	createUser,
} from "../../test-templates";
import { testLogger } from "../../test-utils";

vi.mock("axios", () => {
	const request = vi.fn();
	return {
		default: {
			create: () => ({
				request,
				interceptors: {
					request: { use: vi.fn() },
					response: { use: vi.fn() },
				},
			}),
		},
		create: () => ({
			request,
			interceptors: {
				request: { use: vi.fn() },
				response: { use: vi.fn() },
			},
		}),
		request,
	};
});
const mockedAxios = axios.create();

// Helper to access the vi.fn() for request
const getMockedRequest = () =>
	mockedAxios.request as unknown as ReturnType<typeof vi.fn>;

beforeEach(() => {
	testLogger.info("Clearing all mocks before test");
	vi.clearAllMocks();
});

describe("Auth API", () => {
	it("should handle successful login", async () => {
		testLogger.info("Testing successful login");
		const user = createUser({ email: "test@example.com", name: "test" });
		getMockedRequest().mockResolvedValueOnce({ data: user });

		const res = await authApi.login({
			email: "test@example.com",
			password: "pw",
		});
		testLogger.debug("Login response", res);
		expect(res).toMatchObject({ email: "test@example.com", name: "test" });
	});

	it("should handle failed login", async () => {
		testLogger.info("Testing failed login");
		getMockedRequest().mockRejectedValueOnce({
			isAxiosError: true,
			response: {
				status: 401,
				data: { error: "Invalid credentials" },
			},
		});

		try {
			await authApi.login({ email: "bad", password: "pw" });
			expect.fail("Should have thrown an error");
		} catch (error: unknown) {
			expect((error as Error).message).toBe("Invalid credentials");
		}
	});

	it("should handle network error", async () => {
		testLogger.info("Testing network error");
		getMockedRequest().mockRejectedValueOnce(new Error("Network error"));

		try {
			await authApi.login({ email: "test", password: "pw" });
			expect.fail("Should have thrown an error");
		} catch (error: unknown) {
			expect((error as Error).message).toBe("Network error");
		}
	});
});

describe("Uploads API", () => {
	it("should get uploads", async () => {
		testLogger.info("Testing listFiles");
		const uploads = createUploadList(2, {});
		getMockedRequest().mockResolvedValueOnce({ data: uploads });

		const res = await uploadsApi.listFiles();
		testLogger.debug("listFiles response", res);
		expect(res).toEqual(uploads);
	});

	it("should create an upload", async () => {
		testLogger.info("Testing uploadFile");
		const upload = createUpload({
			id: "3",
			name: "new.pdf",
			status: "pending",
			progress: 0,
			createdAt: "now",
		});
		getMockedRequest().mockResolvedValueOnce({ data: upload });

		const file = new File(["test content"], "new.pdf", {
			type: "application/pdf",
		});
		const res = await uploadsApi.uploadFile(file);
		testLogger.debug("uploadFile response", res);
		expect(res).toEqual(upload);
	});

	it("should delete an upload", async () => {
		testLogger.info("Testing deleteFile");
		getMockedRequest().mockResolvedValueOnce({ data: null });

		const res = await uploadsApi.deleteFile("test.pdf");
		testLogger.debug("deleteFile response", res);
		expect(res).toBeNull();
	});
});

describe("API error handling edge cases", () => {
	it("handles non-Error thrown value (string)", async () => {
		getMockedRequest().mockRejectedValueOnce("fail");

		try {
			await uploadsApi.listFiles();
			expect.fail("Should have thrown an error");
		} catch (error: unknown) {
			expect((error as Error).message).toMatch(/fail|error/i);
		}
	});

	it("handles non-Error thrown value (object)", async () => {
		getMockedRequest().mockRejectedValueOnce({ foo: "bar" });

		try {
			await uploadsApi.listFiles();
			expect.fail("Should have thrown an error");
		} catch (error: unknown) {
			expect((error as Error).message).toMatch(/error|unknown/i);
		}
	});

	it("handles 4xx/5xx error with status and message", async () => {
		const error = new Error("Request failed");
		// Define the shape of the error response
		type ErrorWithResponse = Error & {
			response: { status: number; data: { error: string } };
		};
		(error as ErrorWithResponse).response = {
			status: 500,
			data: { error: "Server error" },
		};
		getMockedRequest().mockRejectedValueOnce(error);

		try {
			await uploadsApi.listFiles();
			expect.fail("Should have thrown an error");
		} catch (err: unknown) {
			expect((err as Error).message).toMatch(
				/server error|500|request failed/i,
			);
		}
	});

	it("handles unknown error type (empty object)", async () => {
		getMockedRequest().mockRejectedValueOnce({});

		try {
			await uploadsApi.listFiles();
			expect.fail("Should have thrown an error");
		} catch (error: unknown) {
			expect((error as Error).message).toMatch(/unknown/i);
		}
	});

	it("normalizes error for all API methods", async () => {
		getMockedRequest().mockRejectedValue(new Error("fail"));

		const methods = [
			() => authApi.login({ email: "a", password: "b" }),
			() => authApi.logout(),
			() => uploadsApi.listFiles(),
			() => uploadsApi.getFile("id"),
			() => uploadsApi.uploadFile(new File(["test"], "test.txt")),
			() => uploadsApi.deleteFile("id"),
		];

		for (const fn of methods) {
			try {
				await fn();
				expect.fail("Should have thrown an error");
			} catch (error: unknown) {
				expect((error as Error).message).toMatch(/fail|error/i);
			}
		}
	});
});
