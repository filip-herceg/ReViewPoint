import React, { Suspense } from "react";
import {
	createBrowserRouter,
	Navigate,
	Outlet,
	RouterProvider,
} from "react-router-dom";
import { ErrorBoundary } from "@/components/ui/error-boundary";

// Import pages with lazy loading for code splitting
const HomePage = React.lazy(() => import("@/pages/HomePage"));
const DashboardPage = React.lazy(
	() => import("@/pages/dashboard/DashboardPage"),
);
const UploadsPage = React.lazy(() => import("@/pages/uploads/UploadsPage"));
const UploadDetailPage = React.lazy(
	() => import("@/pages/uploads/UploadDetailPage"),
);
const NewUploadPage = React.lazy(() => import("@/pages/uploads/NewUploadPage"));
const ReviewsPage = React.lazy(() => import("@/pages/reviews/ReviewsPage"));
const ReviewDetailPage = React.lazy(
	() => import("@/pages/reviews/ReviewDetailPage"),
);
const LoginPage = React.lazy(() => import("@/pages/auth/LoginPage"));
const RegisterPage = React.lazy(() => import("@/pages/auth/RegisterPage"));
const ForgotPasswordPage = React.lazy(
	() => import("@/pages/auth/ForgotPasswordPage"),
);
const ResetPasswordPage = React.lazy(
	() => import("@/pages/auth/ResetPasswordPage"),
);
const ProfilePage = React.lazy(() => import("@/pages/ProfilePage"));
const SettingsPage = React.lazy(() => import("@/pages/SettingsPage"));
const FileDashboardTestPage = React.lazy(
	() => import("@/pages/settings/FileDashboardTestPage"),
);

// Admin and Moderation pages
const AdminPanelPage = React.lazy(() => import("@/pages/admin/AdminPanelPage"));
const UserManagementPage = React.lazy(
	() => import("@/pages/admin/UserManagementPage"),
);
const ModerationPanelPage = React.lazy(
	() => import("@/pages/moderation/ModerationPanelPage"),
);

// Marketplace pages
const MarketplacePage = React.lazy(
	() => import("@/pages/marketplace/MarketplacePage"),
);
const ModuleDetailPage = React.lazy(
	() => import("@/pages/marketplace/ModuleDetailPage"),
);
const MyModulesPage = React.lazy(
	() => import("@/pages/marketplace/MyModulesPage"),
);

// Layout components
import { AppShell } from "@/components/layout/AppShell";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { SkeletonLoader } from "@/components/ui/skeleton-loader";
import { ProtectedRoute } from "./ProtectedRoute";

// Loading fallback component
function PageLoadingFallback() {
	return (
		<div className="flex items-center justify-center min-h-screen">
			<SkeletonLoader variant="card" className="max-w-4xl w-full mx-auto" />
		</div>
	);
}

// Route wrapper with error boundary and suspense
function RouteWrapper({ children }: { children: React.ReactNode }) {
	return (
		<ErrorBoundary>
			<Suspense fallback={<PageLoadingFallback />}>{children}</Suspense>
		</ErrorBoundary>
	);
}

// Create the router configuration
export const router = createBrowserRouter([
	{
		path: "/",
		element: (
			<RouteWrapper>
				<AppShell>
					<Outlet />
				</AppShell>
			</RouteWrapper>
		),
		children: [
			{
				index: true,
				element: <HomePage />,
			},
			{
				path: "dashboard",
				element: (
					<ProtectedRoute>
						<DashboardPage />
					</ProtectedRoute>
				),
			},
			{
				path: "uploads",
				children: [
					{
						index: true,
						element: (
							<ProtectedRoute>
								<UploadsPage />
							</ProtectedRoute>
						),
					},
					{
						path: "new",
						element: (
							<ProtectedRoute>
								<NewUploadPage />
							</ProtectedRoute>
						),
					},
					{
						path: ":id",
						element: (
							<ProtectedRoute>
								<UploadDetailPage />
							</ProtectedRoute>
						),
					},
				],
			},
			{
				path: "reviews",
				children: [
					{
						index: true,
						element: (
							<ProtectedRoute>
								<ReviewsPage />
							</ProtectedRoute>
						),
					},
					{
						path: ":id",
						element: (
							<ProtectedRoute>
								<ReviewDetailPage />
							</ProtectedRoute>
						),
					},
				],
			},
			{
				path: "profile",
				element: (
					<ProtectedRoute>
						<ProfilePage />
					</ProtectedRoute>
				),
			},
			{
				path: "settings",
				element: (
					<ProtectedRoute>
						<SettingsPage />
					</ProtectedRoute>
				),
				children: [
					{
						path: "file-dashboard-test",
						element: (
							<ProtectedRoute>
								<FileDashboardTestPage />
							</ProtectedRoute>
						),
					},
				],
			},
			{
				path: "admin",
				element: (
					<ProtectedRoute roles={["admin"]}>
						<AdminPanelPage />
					</ProtectedRoute>
				),
				children: [
					{
						path: "users",
						element: (
							<ProtectedRoute roles={["admin"]}>
								<UserManagementPage />
							</ProtectedRoute>
						),
					},
				],
			},
			{
				path: "moderation",
				element: (
					<ProtectedRoute roles={["admin", "moderator"]}>
						<ModerationPanelPage />
					</ProtectedRoute>
				),
			},
			{
				path: "marketplace",
				children: [
					{
						index: true,
						element: (
							<ProtectedRoute>
								<MarketplacePage />
							</ProtectedRoute>
						),
					},
					{
						path: "modules/:moduleId",
						element: (
							<ProtectedRoute>
								<ModuleDetailPage />
							</ProtectedRoute>
						),
					},
				],
			},
			{
				path: "my-modules",
				children: [
					{
						index: true,
						element: (
							<ProtectedRoute>
								<MyModulesPage />
							</ProtectedRoute>
						),
					},
				],
			},
		],
	},
	{
		path: "/auth",
		element: (
			<RouteWrapper>
				<AuthLayout>
					<Outlet />
				</AuthLayout>
			</RouteWrapper>
		),
		children: [
			{
				index: true,
				element: <Navigate to="/auth/login" replace />,
			},
			{
				path: "login",
				element: <LoginPage />,
			},
			{
				path: "register",
				element: <RegisterPage />,
			},
			{
				path: "forgot-password",
				element: <ForgotPasswordPage />,
			},
			{
				path: "reset-password",
				element: <ResetPasswordPage />,
			},
		],
	},
	{
		path: "*",
		element: (
			<RouteWrapper>
				<div className="flex flex-col items-center justify-center min-h-screen p-4">
					<h1 className="text-2xl font-bold text-gray-800 mb-2">
						404 - Page Not Found
					</h1>
					<p className="text-gray-600 mb-4">
						The page you're looking for doesn't exist.
					</p>
					<a
						href="/"
						className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
					>
						Go Home
					</a>
				</div>
			</RouteWrapper>
		),
	},
]);

// Main router component to be used in App.tsx
export function AppRouter() {
	return <RouterProvider router={router} />;
}
