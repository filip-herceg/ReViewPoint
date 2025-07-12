import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import UploadForm from "@/components/UploadForm";
import * as uploadStoreModule from "@/lib/store/uploadStore";
import { createUploadFormData, createTestError } from "../test-templates";
import { testLogger } from "../test-utils";
import { createUpload } from "@/lib/api";

// Spy on the store
let useUploadStoreSpy: ReturnType<typeof vi.spyOn>;

function setupUseUploadStoreMock(
  storeOverrides: Partial<
    ReturnType<typeof uploadStoreModule.useUploadStore>
  > = {},
) {
  const store = {
    createUpload: vi.fn(),
    loading: false,
    error: null,
    ...storeOverrides,
  };
  if (useUploadStoreSpy) useUploadStoreSpy.mockRestore();
  useUploadStoreSpy = vi
    .spyOn(uploadStoreModule, "useUploadStore")
    .mockReturnValue(store as any);
  return store;
}

// Utility to render UploadForm with custom store values
function renderUploadFormWithStore(
  storeOverrides: Partial<ReturnType<typeof uploadStoreModule.useUploadStore>>,
) {
  const store = setupUseUploadStoreMock(storeOverrides);
  testLogger.info("Rendering UploadForm with store overrides", storeOverrides);
  return render(<UploadForm />);
}

describe("UploadForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    if (useUploadStoreSpy) useUploadStoreSpy.mockRestore();
  });

  it("renders and submits form data", async () => {
    const formData = createUploadFormData();
    testLogger.debug("Test: renders and submits form data", formData);
    const store = setupUseUploadStoreMock();
    render(<UploadForm />);
    const input = screen.getByLabelText(/file name/i);
    fireEvent.change(input, { target: { value: formData.name } });
    testLogger.info("Changed input value", { value: formData.name });
    const button = screen.getByRole("button", { name: /add upload/i });
    expect(button).not.toBeDisabled();
    fireEvent.click(button);
    testLogger.info("Clicked submit button");
    expect(store.createUpload).toHaveBeenCalledWith({
      name: formData.name,
      status: "pending",
      progress: 0,
    });
  });
  it("shows error from store", () => {
    renderUploadFormWithStore({
      error: {
        type: "unknown",
        message: "Something went wrong",
        original: "test",
      },
    });
    expect(
      screen.getByText(/error: something went wrong/i),
    ).toBeInTheDocument();
  });

  it("shows local error on createUpload rejection", async () => {
    const store = setupUseUploadStoreMock({
      createUpload: vi.fn().mockRejectedValue(createTestError("Local error!")),
    });
    render(<UploadForm />);
    const input = screen.getByLabelText(/file name/i);
    fireEvent.change(input, { target: { value: "fail.pdf" } });
    const button = screen.getByRole("button", { name: /add upload/i });
    fireEvent.click(button);
    // Wait for error to appear
    expect(await screen.findByText(/error: local error!/i)).toBeInTheDocument();
  });

  it("disables submit button when loading", () => {
    testLogger.debug("Test: disables submit button when loading");
    renderUploadFormWithStore({ loading: true });
    const button = screen.getByRole("button") as HTMLButtonElement;
    testLogger.info("Checked button disabled state", {
      disabled: button.disabled,
    });
    expect(button).toBeDisabled();
  });

  it("does not submit if name is empty", () => {
    const store = setupUseUploadStoreMock();
    render(<UploadForm />);
    const button = screen.getByRole("button", { name: /add upload/i });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(store.createUpload).not.toHaveBeenCalled();
  });

  it("shows store error for non-Error values (object, number)", () => {
    renderUploadFormWithStore({ error: { message: "Obj error" } as any });
    expect(screen.getByText(/error: obj error/i)).toBeInTheDocument();
    renderUploadFormWithStore({ error: 42 as any });
    expect(screen.getByText(/error: 42/i)).toBeInTheDocument();
  });

  it("clears local error after successful submit", async () => {
    const store = setupUseUploadStoreMock({
      createUpload: vi
        .fn()
        .mockRejectedValueOnce(createTestError("fail"))
        .mockResolvedValueOnce(undefined),
    });
    render(<UploadForm />);
    const input = screen.getByLabelText(/file name/i);
    fireEvent.change(input, { target: { value: "fail.pdf" } });
    const button = screen.getByRole("button", { name: /add upload/i });
    fireEvent.click(button);
    expect(await screen.findByText(/error: fail/i)).toBeInTheDocument();
    // Fix input and submit again
    fireEvent.change(input, { target: { value: "ok.pdf" } });
    fireEvent.click(button);
    // Wait for error to disappear
    await screen.findByRole("button", { name: /add upload/i });
    expect(screen.queryByText(/error: fail/i)).not.toBeInTheDocument();
  });
});
