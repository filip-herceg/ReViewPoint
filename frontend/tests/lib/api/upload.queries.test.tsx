import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { http } from "msw";
import { beforeEach, describe, expect, it } from "vitest";
import * as uploadQueries from "@/lib/api/upload.queries";
import { server } from "../../msw-server";
import { clearReactQueryCache } from "../../test-templates";
import { testLogger } from "../../test-utils";

describe("upload.queries", () => {
	beforeAll(() => {
		testLogger.info("Starting MSW server");
		server.listen();
	});
	afterAll(() => {
		testLogger.info("Closing MSW server");
		server.close();
	});
	let _queryClient: QueryClient;
	beforeEach(() => {
		testLogger.info(
			"Resetting handlers, QueryClient, clearing mocks, and clearing react-query cache before test",
		);
		server.resetHandlers();
		vi.resetModules();
		vi.clearAllMocks();
		clearReactQueryCache();
		_queryClient = new QueryClient({
			defaultOptions: {
				queries: {
					retry: false,
					networkMode: "always",
				},
				mutations: {
					networkMode: "always",
				},
			},
		});
	});

	describe("fetches uploads (useUploads)", () => {
		it("should return uploads array", async () => {
			testLogger.info("Testing useUploads returns uploads array");
			const queryClient = new QueryClient({
				defaultOptions: {
					queries: {
						retry: false,
						networkMode: "always",
					},
					mutations: {
						networkMode: "always",
					},
				},
			});
			const createWrapper = () => {
				return ({ children }: { children: React.ReactNode }) => (
					<QueryClientProvider client={queryClient}>
						{children}
					</QueryClientProvider>
				);
			};
			const { result } = renderHook(() => uploadQueries.useUploads(), {
				wrapper: createWrapper(),
			});
			await waitFor(() => result.current.status === "success", {
				timeout: 2000,
			});
			const data = result.current.data ?? [];
			testLogger.debug("Fetched uploads data", data);
			testLogger.debug("Full result.current", result.current);
			expect(Array.isArray(data)).toBe(true);
			expect(data).not.toBeNull();
			// Patch: If data is empty, refetch and wait again (workaround for race)
			if (data.length === 0) {
				testLogger.warn("Data array was empty, refetching and waiting again");
				await act(async () => {
					await result.current.refetch?.();
				});
				await waitFor(
					() =>
						Array.isArray(result.current.data) &&
						result.current.data.length === 1,
					{ timeout: 2000 },
				);
			}
			const finalData = result.current.data ?? [];
			expect(finalData).toHaveLength(1);
			const expectedUpload = {
				id: "file.pdf",
				name: "file.pdf",
				status: "completed",
				progress: 100,
				createdAt: expect.any(String),
				response: { filename: "file.pdf", url: "/uploads/file.pdf" },
			};
			testLogger.debug("Expected upload", expectedUpload);
			expect(finalData[0]).toMatchObject(expectedUpload);
		});
	});

	describe("handles error in useUploads", () => {
		it("should return error", async () => {
			testLogger.info("Testing useUploads error handling");
			// Override the handler to return an error for BOTH /uploads and /api/uploads
			server.use(
				http.get("/uploads", () => {
					return new Response("fail", {
						status: 500,
						headers: { "Content-Type": "text/plain" },
					});
				}),
				http.get("/api/uploads", () => {
					return new Response("fail", {
						status: 500,
						headers: { "Content-Type": "text/plain" },
					});
				}),
			);
			const queryClient = new QueryClient({
				defaultOptions: {
					queries: {
						retry: false,
						networkMode: "always",
					},
					mutations: {
						networkMode: "always",
					},
				},
			});
			const createWrapper = () => {
				return ({ children }: { children: React.ReactNode }) => (
					<QueryClientProvider client={queryClient}>
						{children}
					</QueryClientProvider>
				);
			};
			const { result } = renderHook(() => uploadQueries.useUploads(), {
				wrapper: createWrapper(),
			});
			await waitFor(() => result.current.status === "error", { timeout: 3000 });
			testLogger.debug("useUploads error", result.current.error);
			testLogger.debug("Full result.current", result.current);
			// Patch: If error is null, refetch and wait again (workaround for race)
			if (result.current.error == null && (await result.current.refetch())) {
				testLogger.warn("Error was null, refetching and waiting again");
				await act(async () => {
					await result.current.refetch();
				});
				await waitFor(
					() =>
						result.current.status === "error" && result.current.error != null,
					{ timeout: 3000 },
				);
			}
			expect(result.current.error).toBeInstanceOf(Error);
			expect(result.current.error?.message).toBe("fail");
		}, 7000);
	});

	describe("fetches single upload (useUpload)", () => {
		it("should return single upload", async () => {
			testLogger.info("Testing useUpload returns single upload");
			const queryClient = new QueryClient({
				defaultOptions: {
					queries: {
						retry: false,
						networkMode: "always",
					},
					mutations: {
						networkMode: "always",
					},
				},
			});
			const createWrapper = () => {
				return ({ children }: { children: React.ReactNode }) => (
					<QueryClientProvider client={queryClient}>
						{children}
					</QueryClientProvider>
				);
			};
			const { result } = renderHook(() => uploadQueries.useUpload("1"), {
				wrapper: createWrapper(),
			});
			await waitFor(() => result.current.status === "success", {
				timeout: 2000,
			});
			testLogger.debug("Fetched single upload", result.current.data);
			testLogger.debug("Full result.current", result.current);
			// Patch: If data is undefined, refetch and wait again (workaround for race)
			if (!result.current.data) {
				testLogger.warn(
					"Single upload data was undefined, refetching and waiting again",
				);
				await act(async () => {
					await result.current.refetch();
				});
				await waitFor(
					() =>
						result.current.status === "success" &&
						result.current.data &&
						result.current.data.filename === "file.pdf",
					{ timeout: 2000 },
				);
			}
			const expectedUpload = { filename: "file.pdf", url: "/uploads/file.pdf" };
			expect(result.current.data).toEqual(expectedUpload);
		});
	});

	it("createUpload mutation works", async () => {
		testLogger.info("Testing createUpload mutation");
		const { QueryClient, QueryClientProvider } = await import(
			"@tanstack/react-query"
		);
		const queryClient = new QueryClient({
			defaultOptions: {
				queries: {
					retry: false,
					networkMode: "always",
				},
				mutations: {
					networkMode: "always",
				},
			},
		});
		const createWrapper = () => {
			return ({ children }: { children: React.ReactNode }) => (
				<QueryClientProvider client={queryClient}>
					{children}
				</QueryClientProvider>
			);
		};
		const { uploadsApi } = await import("@/lib/api");
		vi.spyOn(uploadsApi, "uploadFile").mockResolvedValueOnce({
			filename: "new.pdf",
			url: "/uploads/new.pdf",
		});
		const uploadQueries = await import("@/lib/api/upload.queries");
		const { result } = renderHook(() => uploadQueries.useCreateUpload(), {
			wrapper: createWrapper(),
		});
		await act(async () => {
			const file = new File(["test content"], "new.pdf", {
				type: "application/pdf",
			});
			const res = await result.current.mutateAsync(file);
			testLogger.debug("createUpload mutation result", res);
			expect(res).toEqual({ filename: "new.pdf", url: "/uploads/new.pdf" });
		});
	});

	it("updateUpload mutation throws error", async () => {
		testLogger.info("Testing updateUpload mutation throws error");
		const { QueryClient, QueryClientProvider } = await import(
			"@tanstack/react-query"
		);
		const queryClient = new QueryClient({
			defaultOptions: {
				queries: {
					retry: false,
					networkMode: "always",
				},
				mutations: {
					networkMode: "always",
				},
			},
		});
		const createWrapper = () => {
			return ({ children }: { children: React.ReactNode }) => (
				<QueryClientProvider client={queryClient}>
					{children}
				</QueryClientProvider>
			);
		};
		const uploadQueries = await import("@/lib/api/upload.queries");
		const { result } = renderHook(() => uploadQueries.useUpdateUpload(), {
			wrapper: createWrapper(),
		});
		await act(async () => {
			try {
				await result.current.mutateAsync({
					id: "1",
					data: { status: "completed", progress: 100 },
				});
				expect.fail("Should have thrown an error");
			} catch (error: any) {
				testLogger.debug("updateUpload mutation error", error);
				expect(error.message).toBe(
					"File updates are not supported. Please delete and re-upload the file.",
				);
			}
		});
	});

	it("deleteUpload mutation works", async () => {
		testLogger.info("Testing deleteUpload mutation");
		const { QueryClient, QueryClientProvider } = await import(
			"@tanstack/react-query"
		);
		const queryClient = new QueryClient({
			defaultOptions: {
				queries: {
					retry: false,
					networkMode: "always",
				},
				mutations: {
					networkMode: "always",
				},
			},
		});
		const createWrapper = () => {
			return ({ children }: { children: React.ReactNode }) => (
				<QueryClientProvider client={queryClient}>
					{children}
				</QueryClientProvider>
			);
		};
		const { uploadsApi } = await import("@/lib/api");
		vi.spyOn(uploadsApi, "deleteFile").mockResolvedValueOnce(null);
		const uploadQueries = await import("@/lib/api/upload.queries");
		const { result } = renderHook(() => uploadQueries.useDeleteUpload(), {
			wrapper: createWrapper(),
		});
		await act(async () => {
			const res = await result.current.mutateAsync("test.pdf");
			testLogger.debug("deleteUpload mutation result", res);
			expect(res).toBeNull();
		});
	});
});
