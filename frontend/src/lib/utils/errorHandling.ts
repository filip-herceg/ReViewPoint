// Utility for error handling in non-API/UI contexts
// Consistent with API error handling and test error normalization

export function getErrorMessage(error: unknown): string {
	// Handle null or undefined
	if (error === null || error === undefined) return "Unknown error";

	// Handle primitive types
	if (typeof error === "string") return error;
	if (typeof error === "number" || typeof error === "boolean")
		return String(error);

	// Handle arrays
	if (Array.isArray(error)) return "Unknown error type";

	// Handle plain objects with error info
	if (typeof error === "object" && !Array.isArray(error)) {
		// Check for common error properties
		const errorObj = error as Record<string, any>;

		// Look for error message in common properties
		if (errorObj.message && typeof errorObj.message === "string") {
			return errorObj.message;
		}

		if (errorObj.error) {
			if (typeof errorObj.error === "string") {
				return errorObj.error;
			}
			// Handle nested error objects
			if (typeof errorObj.error === "object" && errorObj.error !== null) {
				if (
					errorObj.error.message &&
					typeof errorObj.error.message === "string"
				) {
					return errorObj.error.message;
				}
			}
		}

		// Try to convert object to string representation, but fallback to default
		try {
			const errorString = JSON.stringify(error);
			if (errorString && errorString !== "{}") {
				// For objects without meaningful error properties, use fallback
				if (!("message" in error) && !("error" in error)) {
					return "Unknown error type";
				}
				return errorString;
			}
		} catch (_e) {
			// If JSON stringify fails, continue to default
		}

		// Fallback for objects without meaningful error properties
		return "Unknown error type";
	}

	// Fallback for any other type
	return "Unknown error type";
}
