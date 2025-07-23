import { create } from "zustand";
import { uploadsApi } from "@/lib/api";
import { type HandledError, handleApiError } from "@/lib/api/errorHandling";
import type {
	Upload,
	UploadCreateRequest,
	UploadStatus,
} from "@/lib/api/types";
import { validateUploadStatus } from "@/lib/api/types/upload";

interface UploadState {
	uploads: Upload[];
	currentUpload: Upload | null;
	loading: boolean;
	error: HandledError | null;
	addUpload: (upload: Upload) => void;
	updateUpload: (id: string, data: Partial<Upload>) => void;
	setCurrentUpload: (upload: Upload | null) => void;
	fetchUploads: () => Promise<void>;
	createUpload: (upload: UploadCreateRequest) => Promise<void>;
	patchUpload: (id: string, data: Partial<Upload>) => Promise<void>;
	removeUpload: (id: string) => Promise<void>;
}

export const useUploadStore = create<UploadState>((set, get) => ({
	uploads: [],
	currentUpload: null,
	loading: false,
	error: null,
	addUpload: (upload) => {
		if (!upload || typeof upload !== "object" || !upload.id) {
			throw new Error("Invalid upload object passed to addUpload");
		}
		set((state) => ({ uploads: [...state.uploads, upload] }));
	},
	updateUpload: (id, data) => {
		if (!id || typeof id !== "string") {
			throw new Error("Invalid id passed to updateUpload");
		}
		set((state) => ({
			uploads: state.uploads.map((u) => (u.id === id ? { ...u, ...data } : u)),
		}));
	},
	setCurrentUpload: (upload) => {
		if (upload !== null && (!upload.id || typeof upload.id !== "string")) {
			throw new Error("Invalid upload object passed to setCurrentUpload");
		}
		set({ currentUpload: upload });
	},
	fetchUploads: async () => {
		set({ loading: true, error: null });
		try {
			const res = await uploadsApi.listFiles();
			console.debug("API response for fetchUploads:", res);
			// Ensure res.files is an array before mapping
			const uploads: Upload[] = Array.isArray(res.files)
				? res.files.map((file) => ({
						id:
							file.filename ||
							`file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
						name: file.filename || "Unknown File",
						status: validateUploadStatus(file.status || "")
							? (file.status as UploadStatus)
							: "completed",
						progress: typeof file.progress === "number" ? file.progress : 100,
						createdAt: file.createdAt || new Date().toISOString(),
						response: file.url
							? { filename: file.filename, url: file.url }
							: undefined,
					}))
				: [];
			console.debug("Transformed uploads for fetchUploads:", uploads);
			set({ uploads, loading: false });
		} catch (err) {
			const handledError = handleApiError(err);
			set({ error: handledError, loading: false });
		}
	},
	createUpload: async (upload: UploadCreateRequest) => {
		set({ loading: true, error: null });
		try {
			console.debug("Input to createUpload:", upload);
			if (!upload || typeof upload !== "object" || !upload.name) {
				throw new Error("Invalid upload object passed to createUpload");
			}

			// Simulate async work to ensure loading state is observable
			await new Promise((resolve) => setTimeout(resolve, 0));

			// Create a new upload entry in the frontend state
			const newUpload: Upload = {
				id:
					upload.id ||
					`upload-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
				name: upload.name,
				status: validateUploadStatus(upload.status) ? upload.status : "pending",
				progress: upload.progress || 0,
				createdAt: upload.createdAt || new Date().toISOString(),
				...(upload.size ? { size: upload.size } : {}),
				...(upload.type ? { type: upload.type } : {}),
			};
			console.debug("New upload created in createUpload:", newUpload);
			set((state) => ({
				uploads: [...state.uploads, newUpload],
				loading: false,
			}));
		} catch (err) {
			const handledError = handleApiError(err);
			set({ error: handledError, loading: false });
		}
	},
	patchUpload: async (id, data) => {
		set({ loading: true, error: null });
		try {
			if (!id || typeof id !== "string") {
				throw new Error("Invalid id passed to patchUpload");
			}
			// Call the API to patch the upload
			await uploadsApi.patchFile(id, data);
			// Update upload in frontend state
			set((state) => ({
				uploads: state.uploads.map((u) =>
					u.id === id ? { ...u, ...data } : u,
				),
				loading: false,
			}));
		} catch (err) {
			const handledError = handleApiError(err);
			set({ error: handledError, loading: false });
		}
	},
	removeUpload: async (id) => {
		set({ loading: true, error: null });
		try {
			if (!id || typeof id !== "string") {
				throw new Error("Invalid id passed to removeUpload");
			}
			// For file deletion by filename, we need to find the upload to get its name
			const upload = get().uploads.find((u) => u.id === id);
			if (upload) {
				// Use the upload name as filename for deletion
				await uploadsApi.deleteFile(upload.name);
			}
			// Remove from frontend state
			set((state) => ({
				uploads: state.uploads.filter((u) => u.id !== id),
				loading: false,
			}));
		} catch (err) {
			const handledError = handleApiError(err);
			set({ error: handledError, loading: false });
		}
	},
}));
