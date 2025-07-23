import { beforeEach, describe, expect, it } from "vitest";
import { useUploadStore } from "@/lib/store/uploadStore";
import { createUpload } from "../../test-templates";
import { testLogger } from "../../test-utils";

const resetUploadStore = () => {
	testLogger.info("Resetting upload store state");
	useUploadStore.setState({
		uploads: [],
		currentUpload: null,
		loading: false,
		error: null,
	});
};

describe("uploadStore (sync actions)", () => {
	it("should have loading and error state", () => {
		testLogger.info("Checking initial loading and error state");
		const state = useUploadStore.getState();
		testLogger.debug("Initial state", state);
		expect(state.loading).toBe(false);
		expect(state.error).toBeNull();
	});
	beforeEach(() => {
		resetUploadStore();
	});

	it("should have initial state", () => {
		testLogger.info("Checking initial uploads and currentUpload state");
		const state = useUploadStore.getState();
		testLogger.debug("Initial state", state);
		expect(state.uploads).toEqual([]);
		expect(state.currentUpload).toBeNull();
	});

	it("should add an upload", () => {
		testLogger.info("Testing addUpload");
		const upload = createUpload({ status: "pending", progress: 0 });
		useUploadStore.getState().addUpload(upload);
		testLogger.debug(
			"Uploads after addUpload",
			useUploadStore.getState().uploads,
		);
		expect(useUploadStore.getState().uploads).toContainEqual(upload);
	});

	it("should update an upload", () => {
		testLogger.info("Testing updateUpload");
		const upload = createUpload({ status: "pending", progress: 0 });
		useUploadStore.getState().addUpload(upload);
		useUploadStore
			.getState()
			.updateUpload(upload.id, { status: "completed", progress: 100 });
		const updated = useUploadStore
			.getState()
			.uploads.find((u) => u.id === upload.id);
		testLogger.debug("Upload after updateUpload", updated);
		expect(updated?.status).toBe("completed");
		expect(updated?.progress).toBe(100);
	});

	it("should set current upload", () => {
		testLogger.info("Testing setCurrentUpload");
		const upload = createUpload({ status: "pending", progress: 0 });
		useUploadStore.getState().setCurrentUpload(upload);
		testLogger.debug(
			"Current upload after setCurrentUpload(upload)",
			useUploadStore.getState().currentUpload,
		);
		expect(useUploadStore.getState().currentUpload).toEqual(upload);
		useUploadStore.getState().setCurrentUpload(null);
		testLogger.debug(
			"Current upload after setCurrentUpload(null)",
			useUploadStore.getState().currentUpload,
		);
		expect(useUploadStore.getState().currentUpload).toBeNull();
	});
});
