// Main API exports
// This provides a clean structure mirroring the backend API organization

export { authApi } from "./auth";
// Re-export base utilities
export { request } from "./base";
export { healthApi } from "./health";
export { uploadsApi } from "./uploads";
// Users sub-module exports
export { usersCoreApi } from "./users/core";
export { usersExportsApi } from "./users/exports";
export { usersTestOnlyApi } from "./users/test_only_router";
