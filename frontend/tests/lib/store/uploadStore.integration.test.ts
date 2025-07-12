import { useUploadStore } from "@/lib/store/uploadStore";
import { createUpload, createUploadList } from "../../test-templates";
import { testLogger } from "../../test-utils";
import axios from "axios";

vi.mock("axios", () => {
  // Provide a mock for axios.create that returns an object with interceptors and request
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
    testLogger.info("Resetting upload store and mocked request before test");
    useUploadStore.setState({
      uploads: [],
      currentUpload: null,
      loading: false,
      error: null,
    });
    getMockedRequest().mockReset();
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchUploads sets uploads on success", async () => {
    testLogger.info("Testing fetchUploads sets uploads on success");
    const uploads = createUploadList(1);

    // Mock the API response structure that matches FileListResponse
    const apiResponse = {
      files: uploads.map((upload) => ({
        filename: upload.name,
        url: `http://example.com/${upload.name}`,
      })),
      total: uploads.length,
    };

    getMockedRequest().mockResolvedValueOnce({
      data: apiResponse,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });

    await useUploadStore.getState().fetchUploads();
    testLogger.debug(
      "Uploads after fetchUploads",
      useUploadStore.getState().uploads,
    );

    // Expected transformed uploads based on the fetchUploads logic
    const expectedUploads = apiResponse.files.map((file) => ({
      id: file.filename,
      name: file.filename,
      status: "completed" as const,
      progress: 100,
      createdAt: expect.any(String),
      response: { filename: file.filename, url: file.url },
    }));

    expect(useUploadStore.getState().uploads).toEqual(expectedUploads);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("createUpload adds upload to state", async () => {
    testLogger.info("Testing createUpload adds upload to state");
    const upload = createUpload({ status: "pending" });
    getMockedRequest().mockResolvedValueOnce({
      data: upload,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });
    await useUploadStore
      .getState()
      .createUpload({
        name: upload.name,
        status: upload.status,
        progress: upload.progress,
      });
    testLogger.debug(
      "Uploads after createUpload",
      useUploadStore.getState().uploads,
    );
    // Check that an upload was added with the correct properties (ID will be different)
    const actualUploads = useUploadStore.getState().uploads;
    expect(actualUploads).toHaveLength(1);
    expect(actualUploads[0].name).toBe(upload.name);
    expect(actualUploads[0].status).toBe(upload.status);
    expect(actualUploads[0].progress).toBe(upload.progress);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("patchUpload updates upload in state", async () => {
    testLogger.info("Testing patchUpload updates upload in state");
    const orig = createUpload({ status: "pending", progress: 0 });
    useUploadStore.setState({ uploads: [orig] });
    const updated = { ...orig, status: "completed", progress: 100 };
    getMockedRequest().mockResolvedValueOnce({
      data: updated,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });
    await useUploadStore
      .getState()
      .patchUpload(orig.id, { status: "completed", progress: 100 });
    testLogger.debug(
      "Uploads after patchUpload",
      useUploadStore.getState().uploads,
    );
    expect(useUploadStore.getState().uploads[0]).toMatchObject({
      status: "completed",
      progress: 100,
    });
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("removeUpload removes upload from state", async () => {
    testLogger.info("Testing removeUpload removes upload from state");
    const orig = createUpload({ status: "pending", progress: 0 });
    useUploadStore.setState({ uploads: [orig] });
    getMockedRequest().mockResolvedValueOnce({
      data: null,
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });
    await useUploadStore.getState().removeUpload(orig.id);
    testLogger.debug(
      "Uploads after removeUpload",
      useUploadStore.getState().uploads,
    );
    expect(useUploadStore.getState().uploads).toHaveLength(0);
    expect(useUploadStore.getState().error).toBeNull();
  });

  it("sets error on API failure", async () => {
    testLogger.info("Testing error state on API failure");
    getMockedRequest().mockRejectedValueOnce({
      isAxiosError: true,
      response: { data: "fail", status: 500 },
    });
    await useUploadStore.getState().fetchUploads();
    const error = useUploadStore.getState().error;
    testLogger.debug("Error after failed fetchUploads", error);
    expect(error).toMatchObject({
      type: "unknown", // Currently becomes unknown due to string extraction
      message: "fail", // The string error message should be preserved
      original: expect.any(Error), // The original should be an Error object
    });
    expect(useUploadStore.getState().loading).toBe(false);
  });
});
