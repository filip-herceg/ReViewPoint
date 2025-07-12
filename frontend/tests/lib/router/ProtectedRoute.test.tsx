/**
 * Tests for Enhanced ProtectedRoute component
 * Verifies role-based route protection and redirection logic
 */

import { render, screen } from "@testing-library/react";
import type React from "react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "@/lib/router/ProtectedRoute";

// Mock the useAuth hook
const mockUseAuth = vi.fn();
vi.mock("@/hooks/useAuth", () => ({
	useAuth: () => mockUseAuth(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
	const actual = await vi.importActual("react-router-dom");
	return {
		...actual,
		Navigate: ({ to, state }: { to: string; state?: any }) => {
			mockNavigate(to, state);
			return (
				<div data-testid="navigate" data-to={to}>
					Redirecting to {to}
				</div>
			);
		},
		useLocation: () => ({ pathname: "/test-path" }),
	};
});

function renderWithRouter(
	component: React.ReactElement,
	initialEntries = ["/"],
) {
	return render(
		<MemoryRouter initialEntries={initialEntries}>{component}</MemoryRouter>,
	);
}

describe("ProtectedRoute", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("Authentication Protection", () => {
		it("renders children when user is authenticated", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("protected-content")).toBeInTheDocument();
		});

		it("redirects to login when user is not authenticated", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: false,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("navigate")).toBeInTheDocument();
			expect(screen.getByTestId("navigate")).toHaveAttribute(
				"data-to",
				"/auth/login",
			);
			expect(mockNavigate).toHaveBeenCalledWith("/auth/login", {
				from: "/test-path",
			});
		});

		it("redirects to custom URL when specified and user not authenticated", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: false,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute redirectTo="/custom-login">
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("navigate")).toHaveAttribute(
				"data-to",
				"/custom-login",
			);
		});
	});

	describe("Role-Based Protection", () => {
		it("renders children when user has any of the required roles", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn().mockReturnValue(true),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin", "moderator"]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("protected-content")).toBeInTheDocument();
		});

		it("redirects when user lacks any required role", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn().mockReturnValue(false),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin"]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("navigate")).toBeInTheDocument();
			expect(screen.getByTestId("navigate")).toHaveAttribute(
				"data-to",
				"/dashboard",
			);
			expect(mockNavigate).toHaveBeenCalledWith("/dashboard", {
				from: "/test-path",
				error: "Access denied. Required role: admin",
			});
		});

		it("redirects when user lacks all required roles (requireAllRoles=true)", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn().mockImplementation((role) => role === "admin"), // Only has admin, not superuser
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin", "superuser"]} requireAllRoles={true}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("navigate")).toBeInTheDocument();
			expect(mockNavigate).toHaveBeenCalledWith("/dashboard", {
				from: "/test-path",
				error: "Access denied. Required roles: admin, superuser",
			});
		});

		it("renders children when user has all required roles (requireAllRoles=true)", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn().mockReturnValue(true), // Has all roles
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin", "superuser"]} requireAllRoles={true}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("protected-content")).toBeInTheDocument();
		});

		it("uses custom unauthorized redirect URL when specified", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn().mockReturnValue(false),
			});

			renderWithRouter(
				<ProtectedRoute
					roles={["admin"]}
					unauthorizedRedirectTo="/access-denied"
				>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("navigate")).toHaveAttribute(
				"data-to",
				"/access-denied",
			);
		});
	});

	describe("Complex Role Scenarios", () => {
		it("handles empty roles array correctly", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute roles={[]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("protected-content")).toBeInTheDocument();
		});

		it("handles single role requirement", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn().mockReturnValue(true),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin"]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(screen.getByTestId("protected-content")).toBeInTheDocument();
		});

		it("handles multiple role requirements correctly", () => {
			const hasAnyRole = vi.fn().mockReturnValue(true);
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole,
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin", "moderator", "supervisor"]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(hasAnyRole).toHaveBeenCalledWith([
				"admin",
				"moderator",
				"supervisor",
			]);
			expect(screen.getByTestId("protected-content")).toBeInTheDocument();
		});
	});

	describe("Error Messages", () => {
		it("generates correct error message for single role", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn().mockReturnValue(false),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin"]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(mockNavigate).toHaveBeenCalledWith("/dashboard", {
				from: "/test-path",
				error: "Access denied. Required role: admin",
			});
		});

		it("generates correct error message for multiple roles", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: true,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn().mockReturnValue(false),
			});

			renderWithRouter(
				<ProtectedRoute roles={["admin", "moderator"]}>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
			);

			expect(mockNavigate).toHaveBeenCalledWith("/dashboard", {
				from: "/test-path",
				error: "Access denied. Required roles: admin, moderator",
			});
		});
	});

	describe("Integration with Location State", () => {
		it("preserves current location in state for return navigation", () => {
			mockUseAuth.mockReturnValue({
				isAuthenticated: false,
				hasRole: vi.fn(),
				hasAnyRole: vi.fn(),
			});

			renderWithRouter(
				<ProtectedRoute>
					<div data-testid="protected-content">Protected Content</div>
				</ProtectedRoute>,
				["/some/protected/path"],
			);

			expect(mockNavigate).toHaveBeenCalledWith("/auth/login", {
				from: "/test-path",
			});
		});
	});
});
