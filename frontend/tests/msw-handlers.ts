import { HttpResponse, http } from "msw";
import logger from "../src/logger";
import { createUpload } from "./test-templates";
export const handlers = [
	// GET /api/uploads/:filename (must come before /api/uploads)
	http.get("/api/uploads/:filename", ({ params }) => {
		const { filename } = params;
		if (filename === "1" || filename === "file.pdf") {
			const data = { filename: "file.pdf", url: "/uploads/file.pdf" };
			logger.info("[MSW] GET /api/uploads/:filename", data);
			return new Response(JSON.stringify(data), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			});
		}
		logger.warn("[MSW] GET /api/uploads/:filename - Not found", { filename });
		return new Response(JSON.stringify({ error: "Not found" }), {
			status: 404,
		});
	}),
	// GET /uploads/:filename (for axios baseURL '/api', this is the actual endpoint hit)
	http.get("/uploads/:filename", ({ params }) => {
		const { filename } = params;
		if (filename === "1" || filename === "file.pdf") {
			const data = { filename: "file.pdf", url: "/uploads/file.pdf" };
			logger.info("[MSW] GET /uploads/:filename", data);
			return new Response(JSON.stringify(data), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			});
		}
		logger.warn("[MSW] GET /uploads/:filename - Not found", { filename });
		return new Response(JSON.stringify({ error: "Not found" }), {
			status: 404,
		});
	}),

	// GET /api/uploads (success and error simulation)
	http.get("/api/uploads", ({ request }) => {
		const url = new URL(request.url);
		if (url.searchParams.get("fail") === "1") {
			logger.warn("[MSW] GET /api/uploads - Simulating error response");
			return new Response(JSON.stringify({ error: "fail" }), { status: 500 });
		}
		const data = {
			files: [{ filename: "file.pdf", url: "/uploads/file.pdf" }],
			total: 1,
		};
		logger.info("[MSW] GET /api/uploads", data);
		return new Response(JSON.stringify(data), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	}),
	// GET /uploads (for axios baseURL '/api', this is the actual endpoint hit)
	http.get("/uploads", ({ request }) => {
		const url = new URL(request.url);
		if (url.searchParams.get("fail") === "1") {
			logger.warn("[MSW] GET /uploads - Simulating error response");
			return new Response(JSON.stringify({ error: "fail" }), { status: 500 });
		}
		const data = {
			files: [{ filename: "file.pdf", url: "/uploads/file.pdf" }],
			total: 1,
		};
		logger.info("[MSW] GET /uploads", data);
		return new Response(JSON.stringify(data), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	}),

	// POST /uploads
	http.post("/api/uploads", async ({ request }) => {
		logger.info("[MSW] POST /api/uploads");
		logger.debug("Request URL:", request.url);
		let body = null;
		try {
			body = await request.json();
			logger.debug("Request body:", body);
		} catch (e) {
			logger.warn("No JSON body or failed to parse:", e);
		}
		const data = createUpload({
			id: "2",
			name: "new.pdf",
			status: "pending",
			progress: 0,
		});
		logger.info("Responding with:", data);
		return new Response(JSON.stringify(data), {
			status: 201,
			headers: { "Content-Type": "application/json" },
		});
	}),
	http.post("/uploads", async ({ request }) => {
		logger.info("[MSW] POST /uploads");
		logger.debug("Request URL:", request.url);
		let body = null;
		try {
			body = await request.json();
			logger.debug("Request body:", body);
		} catch (e) {
			logger.warn("No JSON body or failed to parse:", e);
		}
		const data = createUpload({
			id: "2",
			name: "new.pdf",
			status: "pending",
			progress: 0,
		});
		logger.info("Responding with:", data);
		return new Response(JSON.stringify(data), {
			status: 201,
			headers: { "Content-Type": "application/json" },
		});
	}),

	// PATCH /uploads/:id
	http.patch("/api/uploads/:id", async ({ request, params }) => {
		logger.info("[MSW] PATCH /api/uploads/:id");
		logger.debug("Request URL:", request.url);
		logger.debug("Params:", params);
		let body = null;
		try {
			body = await request.json();
			logger.debug("Request body:", body);
		} catch (e) {
			logger.warn("No JSON body or failed to parse:", e);
		}
		const data = createUpload({
			id: "1",
			name: "file.pdf",
			status: "completed",
			progress: 100,
		});
		logger.info("Responding with:", data);
		return new Response(JSON.stringify(data), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	}),
	http.patch("/uploads/:id", async ({ request, params }) => {
		logger.info("[MSW] PATCH /uploads/:id");
		logger.debug("Request URL:", request.url);
		logger.debug("Params:", params);
		let body = null;
		try {
			body = await request.json();
			logger.debug("Request body:", body);
		} catch (e) {
			logger.warn("No JSON body or failed to parse:", e);
		}
		const data = createUpload({
			id: "1",
			name: "file.pdf",
			status: "completed",
			progress: 100,
		});
		logger.info("Responding with:", data);
		return new Response(JSON.stringify(data), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	}),

	// DELETE /uploads/:id
	http.delete("/api/uploads/:id", async ({ request, params }) => {
		logger.info("[MSW] DELETE /api/uploads/:id");
		logger.debug("Request URL:", request.url);
		logger.debug("Params:", params);
		logger.info("Responding with 204 No Content");
		return new Response(null, { status: 204 });
	}),
	http.delete("/uploads/:id", async ({ request, params }) => {
		logger.info("[MSW] DELETE /uploads/:id");
		logger.debug("Request URL:", request.url);
		logger.debug("Params:", params);
		logger.info("Responding with 204 No Content");
		return new Response(null, { status: 204 });
	}),
	// Fallback handler for unmatched requests to /api/uploads* and /uploads*
	http.all(/\/api\/uploads.*/, ({ request }) => {
		logger.error("[MSW] Unmatched /api/uploads* request:", request.url);
		return HttpResponse.json(
			{ error: "MSW fallback: Not found" },
			{ status: 404 },
		);
	}),
	http.all(/\/uploads.*/, ({ request }) => {
		logger.error("[MSW] Unmatched /uploads* request:", request.url);
		return HttpResponse.json(
			{ error: "MSW fallback: Not found" },
			{ status: 404 },
		);
	}),
];
