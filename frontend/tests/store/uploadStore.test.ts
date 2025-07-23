import { act } from "react-dom/test-utils";
import { vi } from "vitest";
import { useUploadStore } from "@/lib/store/uploadStore";

// Enhance the mock setup to include all required methods
vi.mock("@/lib/api", () => ({
	uploadsApi: {
		patchFile: vi.fn().mockResolvedValue({}),
		deleteFile: vi.fn().mockResolvedValue({}),
		listFiles: vi.fn().mockResolvedValue([]),
		createFile: vi.fn().mockResolvedValue({
			id: "1",
			name: "test.txt",
			status: "pending",
			progress: 0,
			createdAt: new Date().toISOString(),
		}),
	},
	createUpload: vi.fn().mockImplementation(({ name, status, progress }) => ({
		id: "mock-id",
		name,
		status,
		progress,
		createdAt: new Date().toISOString(),
	})),
}));

describe("uploadStore error handling", () => {
	beforeEach(() => {
		// Reset store state before each test
		act(() => {
			useUploadStore.setState({
				uploads: [],
				currentUpload: null,
				loading: false,
				error: null,
			});
		});
	});

	it("throws and sets error for invalid addUpload", () => {
		expect(() => useUploadStore.getState().addUpload(null as never)).toThrow();
	});

	it("throws and sets error for invalid updateUpload", () => {
		expect(() =>
			useUploadStore.getState().updateUpload(undefined as never, {}),
		).toThrow();
	});

	it("throws and sets error for invalid setCurrentUpload", () => {
		expect(() =>
			useUploadStore.getState().setCurrentUpload({} as never),
		).toThrow();
	});

	// Update test cases to ensure proper error handling and state validation
	it("sets error on fetchUploads API error", async () => {
		const { uploadsApi } = await import("@/lib/api");
		uploadsApi.listFiles = vi
			.fn()
			.mockRejectedValue(new Error("API fetch failed"));

		await act(async () => {
			await useUploadStore.getState().fetchUploads();
		});

		expect(useUploadStore.getState().error).toBeTruthy();
		expect(useUploadStore.getState().error?.message).toMatch(
			/API fetch failed/,
		);
	});

	it("sets error on createUpload API error", async () => {
		const { uploadsApi } = await import("@/lib/api");
		uploadsApi.uploadFile = vi
			.fn()
			.mockRejectedValue(new Error("Invalid upload object"));

		await act(async () => {
			await useUploadStore
				.getState()
				.createUpload({ name: "", status: "pending", progress: 0 });
		});

		expect(useUploadStore.getState().error).toBeTruthy();
		expect(useUploadStore.getState().error?.message).toMatch(
			/Invalid upload object/,
		);
	});

	it("sets error on patchUpload API error", async () => {
		const { uploadsApi } = await import("@/lib/api");
		uploadsApi.patchFile = vi.fn().mockRejectedValue(new Error("Patch failed"));

		const upload = {
			id: "1",
			name: "test.txt",
			status: "pending" as const,
			progress: 0,
			createdAt: new Date().toISOString(),
		};
		useUploadStore.getState().addUpload(upload);

		await act(async () => {
			await useUploadStore.getState().patchUpload("1", { name: "updated.txt" });
		});

		expect(useUploadStore.getState().error).toBeTruthy();
		expect(useUploadStore.getState().error?.message).toMatch(/Patch failed/);
	});

	it("sets error on removeUpload API error", async () => {
		const { uploadsApi } = await import("@/lib/api");
		const mockDeleteFile = vi
			.fn()
			.mockRejectedValue(new Error("Delete failed"));
		uploadsApi.deleteFile = mockDeleteFile;

		// Add upload directly to store bypassing the mocked createUpload
		const upload = {
			id: "1",
			name: "test.txt",
			status: "pending" as const,
			progress: 0,
			createdAt: new Date().toISOString(),
		};
		useUploadStore.getState().addUpload(upload);

		// Verify the upload was added
		const uploads = useUploadStore.getState().uploads;
		expect(uploads).toHaveLength(1);
		expect(uploads[0].id).toBe("1");
		expect(uploads[0].name).toBe("test.txt");

		await act(async () => {
			await useUploadStore.getState().removeUpload("1");
		});

		// Verify the mock was called with the correct filename
		expect(mockDeleteFile).toHaveBeenCalledWith("test.txt");
		expect(useUploadStore.getState().error).toBeTruthy();
		expect(useUploadStore.getState().error?.message).toMatch(/Delete failed/);
	});

	it("sets error for invalid patchUpload input", async () => {
		await useUploadStore.getState().patchUpload(undefined as never, {});
		expect(useUploadStore.getState().error).toBeTruthy();
	});

	it("sets error for invalid removeUpload input", async () => {
		await useUploadStore.getState().removeUpload(undefined as never);
		expect(useUploadStore.getState().error).toBeTruthy();
	});
});
