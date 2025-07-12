import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import { useUploadStore } from "@/lib/store/uploadStore";
import { createUpload, createUploadList } from "../../test-templates";
import { testLogger } from "../../test-utils";

import axios from "axios";

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

describe("uploadStore async actions", () => {
  beforeEach(() => {
    testLogger.info("Resetting upload store and clearing mocks before test");
    useUploadStore.setState({
      uploads: [],
      currentUpload: null,
      loading: false,
      error: null,
    });
    vi.clearAllMocks();
  });

  it("fetchUploads sets uploads and loading", async () => {
    testLogger.info("Testing fetchUploads sets uploads and loading");
    const uploads = createUploadList(1, { progress: 0 }); // Specify progress to make test deterministic
    // Mock the API response with files array like the real API returns
    const apiResponse = {
      files: uploads.map((upload) => ({
        filename: upload.name,
        url: `/uploads/${upload.name}`,
        status: upload.status,
        progress: upload.progress,
        createdAt: upload.createdAt,
      })),
      total: uploads.length,
    };
    getMockedRequest().mockResolvedValueOnce({ data: apiResponse });
    const store = useUploadStore.getState();
    const promise = store.fetchUploads();
    testLogger.debug(
      "Loading after fetchUploads called",
      useUploadStore.getState().loading,
    );
    expect(useUploadStore.getState().loading).toBe(true);
    await promise;
    testLogger.debug(
      "Uploads after fetchUploads",
      useUploadStore.getState().uploads,
    );
    // Since the transformation creates new upload objects with different IDs, we need to check the properties
    const actualUploads = useUploadStore.getState().uploads;
    expect(actualUploads).toHaveLength(uploads.length);
    expect(actualUploads[0].name).toBe(uploads[0].name);
    expect(actualUploads[0].status).toBe(uploads[0].status);
    expect(actualUploads[0].progress).toBe(uploads[0].progress);
    expect(useUploadStore.getState().loading).toBe(false);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("createUpload adds upload and sets loading", async () => {
    testLogger.info("Testing createUpload adds upload and sets loading");
    const upload = createUpload({ status: "pending" });
    getMockedRequest().mockResolvedValueOnce({ data: upload });
    const promise = useUploadStore.getState().createUpload({
      id: upload.id,
      name: upload.name,
      status: upload.status,
      progress: upload.progress,
      createdAt: upload.createdAt,
    });
    testLogger.debug(
      "Loading after createUpload called",
      useUploadStore.getState().loading,
    );
    expect(useUploadStore.getState().loading).toBe(true);
    await promise;
    testLogger.debug(
      "Uploads after createUpload",
      useUploadStore.getState().uploads,
    );
    expect(useUploadStore.getState().uploads).toContainEqual(upload);
    expect(useUploadStore.getState().loading).toBe(false);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("patchUpload updates upload and sets loading", async () => {
    testLogger.info("Testing patchUpload updates upload and sets loading");
    const orig = createUpload({ status: "pending", progress: 0 });
    useUploadStore.setState({ uploads: [orig] });
    const updated = { ...orig, status: "completed", progress: 100 };
    getMockedRequest().mockResolvedValueOnce({ data: updated });
    const promise = useUploadStore
      .getState()
      .patchUpload(orig.id, { status: "completed", progress: 100 });
    testLogger.debug(
      "Loading after patchUpload called",
      useUploadStore.getState().loading,
    );
    expect(useUploadStore.getState().loading).toBe(true);
    await promise;
    testLogger.debug(
      "Uploads after patchUpload",
      useUploadStore.getState().uploads,
    );
    expect(useUploadStore.getState().uploads[0]).toMatchObject({
      status: "completed",
      progress: 100,
    });
    expect(useUploadStore.getState().loading).toBe(false);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("removeUpload removes upload and sets loading", async () => {
    testLogger.info("Testing removeUpload removes upload and sets loading");
    const orig = createUpload({ status: "pending", progress: 0 });
    useUploadStore.setState({ uploads: [orig] });
    getMockedRequest().mockResolvedValueOnce({ data: null });
    const promise = useUploadStore.getState().removeUpload(orig.id);
    testLogger.debug(
      "Loading after removeUpload called",
      useUploadStore.getState().loading,
    );
    expect(useUploadStore.getState().loading).toBe(true);
    await promise;
    testLogger.debug(
      "Uploads after removeUpload",
      useUploadStore.getState().uploads,
    );
    expect(useUploadStore.getState().uploads).toHaveLength(0);
    expect(useUploadStore.getState().loading).toBe(false);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("sets error on API failure", async () => {
    testLogger.info("Testing error state on API failure");
    // Mock the request to return a response without data, triggering the "No data in response" error
    getMockedRequest().mockResolvedValueOnce({
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
      // No data field, which will trigger the "No data in response" error
    });
    await useUploadStore.getState().fetchUploads();
    testLogger.debug(
      "Error after failed fetchUploads",
      useUploadStore.getState().error,
    );
    expect(useUploadStore.getState().error).toMatchObject({
      type: "unknown", // Error thrown by uploads.ts becomes unknown type
      message: "No data in response", // The actual error message from uploads.ts
      original: expect.any(Error), // The original error object
    });
    expect(useUploadStore.getState().loading).toBe(false);
  });
});
