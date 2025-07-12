import userEvent from "@testing-library/user-event";

it("shows local error on patchUpload rejection", async () => {
	const uploads = createUploadList(1, {});
	act(() => {
		useUploadStore.setState({
			uploads,
			loading: false,
			error: null,
			patchUpload: vi.fn().mockRejectedValue(new Error("Patch failed!")),
		});
	});
	render(<UploadList disableAutoFetch />);
	// Click edit
	const editBtn = screen.getByRole("button", { name: /edit/i });
	await userEvent.click(editBtn);
	// Change name
	const input = screen.getByDisplayValue(uploads[0].name);
	await userEvent.clear(input);
	await userEvent.type(input, "newname.pdf");
	// Click save
	const saveBtn = screen.getByRole("button", { name: /save/i });
	await userEvent.click(saveBtn);
	// Should show local error
	expect(await screen.findByText(/error: patch failed!/i)).toBeInTheDocument();
});

import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import UploadList from "@/components/UploadList";
import { useUploadStore } from "@/lib/store/uploadStore";
import { clearReactQueryCache, createUploadList } from "../test-templates";
import { testLogger } from "../test-utils";

const globalAny: any = globalThis;

describe("UploadList component", () => {
	beforeEach(() => {
		clearReactQueryCache();
	});
	beforeEach(() => {
		testLogger.info("Resetting upload store and mocking fetch");
		useUploadStore.setState({
			uploads: [],
			currentUpload: null,
			loading: false,
			error: null,
		});
		globalAny.fetch = vi.fn();
	});

	it("shows loading state", () => {
		testLogger.info("Testing loading state");
		act(() => {
			testLogger.debug("Setting loading=true in store");
			useUploadStore.setState({ loading: true });
		});
		render(<UploadList disableAutoFetch />);
		testLogger.debug("Rendered UploadList with loading=true");
		expect(screen.getByText(/loading uploads/i)).toBeInTheDocument();
	});

	it("shows error state", () => {
		testLogger.info("Testing error state");
		act(() => {
			testLogger.debug('Setting error="fail" and loading=false in store');
			useUploadStore.setState({
				error: { type: "unknown", message: "fail" },
				loading: false,
			});
		});
		render(<UploadList disableAutoFetch />);
		testLogger.debug("Rendered UploadList with error state");
		expect(screen.getByText(/error: fail/i)).toBeInTheDocument();
	});

	it("shows empty state", () => {
		testLogger.info("Testing empty state");
		act(() => {
			testLogger.debug(
				"Setting uploads=[] and loading=false, error=null in store",
			);
			useUploadStore.setState({ uploads: [], loading: false, error: null });
		});
		render(<UploadList disableAutoFetch />);
		testLogger.debug("Rendered UploadList with empty uploads");
		expect(screen.getByText(/no uploads found/i)).toBeInTheDocument();
	});

	it("shows uploads", () => {
		testLogger.info("Testing uploads display");
		let uploads: Array<{ name: string; status: string }> = [];
		act(() => {
			const generated = createUploadList(2, {});
			testLogger.debug("Setting uploads in store", generated);
			useUploadStore.setState({
				uploads: generated,
				loading: false,
				error: null,
			});
			uploads = generated;
		});
		render(<UploadList disableAutoFetch />);
		testLogger.debug("Rendered UploadList with uploads", uploads);
		// Use the generated upload names for assertions
		uploads.forEach((upload) => {
			testLogger.debug(
				`Checking for upload name: ${upload.name} and status: ${upload.status}`,
			);
			expect(screen.getByText(upload.name)).toBeInTheDocument();
		});
		// Check that each status appears at least once (handle duplicate statuses)
		const uniqueStatuses = [...new Set(uploads.map((upload) => upload.status))];
		uniqueStatuses.forEach((status) => {
			const statusRegex = new RegExp(status, "i");
			expect(screen.getAllByText(statusRegex).length).toBeGreaterThan(0);
		});
	});

	it("shows store error for non-Error values (object, number)", () => {
		act(() => {
			useUploadStore.setState({
				error: { message: "Obj error" } as any,
				loading: false,
			});
		});
		const { unmount } = render(<UploadList disableAutoFetch />);
		expect(screen.getByText(/error: obj error/i)).toBeInTheDocument();

		unmount(); // Clean up first render

		act(() => {
			useUploadStore.setState({ error: 42 as any, loading: false });
		});
		render(<UploadList disableAutoFetch />);
		expect(screen.getByText(/error: 42/i)).toBeInTheDocument();
	});

	it("shows local error on removeUpload rejection", async () => {
		const uploads = createUploadList(1, {});
		act(() => {
			useUploadStore.setState({
				uploads,
				loading: false,
				error: null,
				removeUpload: vi.fn().mockRejectedValue(new Error("Delete failed!")),
			});
		});
		render(<UploadList disableAutoFetch />);
		const deleteBtn = screen.getByRole("button", { name: /delete/i });
		await userEvent.click(deleteBtn);
		expect(
			await screen.findByText(/error: delete failed!/i),
		).toBeInTheDocument();
	});

	it("clears local error after successful edit/save", async () => {
		const uploads = createUploadList(1, {});
		let callCount = 0;
		act(() => {
			useUploadStore.setState({
				uploads,
				loading: false,
				error: null,
				patchUpload: vi.fn().mockImplementation(() => {
					callCount++;
					if (callCount === 1) return Promise.reject(new Error("fail"));
					return Promise.resolve();
				}),
			});
		});
		render(<UploadList disableAutoFetch />);
		// Edit and fail
		await userEvent.click(screen.getByRole("button", { name: /edit/i }));
		const input = screen.getByDisplayValue(uploads[0].name);
		await userEvent.clear(input);
		await userEvent.type(input, "newname.pdf");
		await userEvent.click(screen.getByRole("button", { name: /save/i }));
		expect(await screen.findByText(/error: fail/i)).toBeInTheDocument();
		// Edit and succeed
		await userEvent.clear(input);
		await userEvent.type(input, "ok.pdf");
		await userEvent.click(screen.getByRole("button", { name: /save/i }));
		expect(screen.queryByText(/error: fail/i)).not.toBeInTheDocument();
	});

	it("clears local error on cancel edit", async () => {
		const uploads = createUploadList(1, {});
		act(() => {
			useUploadStore.setState({
				uploads,
				loading: false,
				error: null,
				patchUpload: vi.fn().mockRejectedValue(new Error("fail")), // always fail
			});
		});
		render(<UploadList disableAutoFetch />);
		await userEvent.click(screen.getByRole("button", { name: /edit/i }));
		const input = screen.getByDisplayValue(uploads[0].name);
		await userEvent.clear(input);
		await userEvent.type(input, "newname.pdf");
		await userEvent.click(screen.getByRole("button", { name: /save/i }));
		expect(await screen.findByText(/error: fail/i)).toBeInTheDocument();
		await userEvent.click(screen.getByRole("button", { name: /cancel/i }));
		expect(screen.queryByText(/error: fail/i)).not.toBeInTheDocument();
	});

	it("does not call patchUpload if edit name is empty", async () => {
		const uploads = createUploadList(1, {});
		const patchUpload = vi.fn();
		act(() => {
			useUploadStore.setState({
				uploads,
				loading: false,
				error: null,
				patchUpload,
			});
		});
		render(<UploadList disableAutoFetch />);
		await userEvent.click(screen.getByRole("button", { name: /edit/i }));
		const input = screen.getByDisplayValue(uploads[0].name);
		await userEvent.clear(input);
		// Save button should be disabled
		const saveBtn = screen.getByRole("button", { name: /save/i });
		expect(saveBtn).toBeDisabled();
		await userEvent.click(saveBtn);
		expect(patchUpload).not.toHaveBeenCalled();
	});
});
