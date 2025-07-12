import { beforeEach, describe, expect, it } from "vitest";
import type { Upload } from "@/lib/api/types";
import { useUploadStore } from "../uploadStore";

const resetUploadStore = () => {
	useUploadStore.setState({ uploads: [], currentUpload: null });
};

describe("uploadStore", () => {
	beforeEach(() => {
		resetUploadStore();
	});

	it("should have initial state", () => {
		const state = useUploadStore.getState();
		expect(state.uploads).toEqual([]);
		expect(state.currentUpload).toBeNull();
	});

	it("should add an upload", () => {
		const upload: Upload = {
			id: "1",
			name: "file.pdf",
			status: "pending",
			progress: 0,
			createdAt: new Date().toISOString(),
		};
		useUploadStore.getState().addUpload(upload);
		expect(useUploadStore.getState().uploads).toContainEqual(upload);
	});

	it("should update an upload", () => {
		const upload: Upload = {
			id: "1",
			name: "file.pdf",
			status: "pending",
			progress: 0,
			createdAt: new Date().toISOString(),
		};
		useUploadStore.getState().addUpload(upload);
		useUploadStore
			.getState()
			.updateUpload("1", { status: "completed", progress: 100 });
		const updated = useUploadStore.getState().uploads.find((u) => u.id === "1");
		expect(updated?.status).toBe("completed");
		expect(updated?.progress).toBe(100);
	});

	it("should set current upload", () => {
		const upload: Upload = {
			id: "1",
			name: "file.pdf",
			status: "pending",
			progress: 0,
			createdAt: new Date().toISOString(),
		};
		useUploadStore.getState().setCurrentUpload(upload);
		expect(useUploadStore.getState().currentUpload).toEqual(upload);
		useUploadStore.getState().setCurrentUpload(null);
		expect(useUploadStore.getState().currentUpload).toBeNull();
	});
});
