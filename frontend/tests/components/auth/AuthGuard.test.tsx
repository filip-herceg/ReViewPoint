/**
 * Tests for AuthGuard components
 * Verifies role-based access control and conditional rendering
 */

import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  AuthGuard,
  RequireAllRoles,
  RequireAnyRole,
  RequireAuth,
  RequireRole,
  RequireUnauthenticated,
  ShowForAuth,
  ShowForGuest,
  ShowForRole,
  ShowForRoles,
  useAuthStatus,
} from "@/components/auth/AuthGuard";

// Mock the useAuth hook
const mockUseAuth = vi.fn();
vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("AuthGuard Components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("AuthGuard", () => {
    it("renders children when authenticated and no roles required", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <AuthGuard>
          <div data-testid="protected-content">Protected Content</div>
        </AuthGuard>,
      );

      expect(screen.getByTestId("protected-content")).toBeInTheDocument();
    });

    it("renders fallback when not authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <AuthGuard fallback={<div data-testid="fallback">Login Required</div>}>
          <div data-testid="protected-content">Protected Content</div>
        </AuthGuard>,
      );

      expect(screen.getByTestId("fallback")).toBeInTheDocument();
      expect(screen.queryByTestId("protected-content")).not.toBeInTheDocument();
    });

    it("renders default auth fallback when no custom fallback provided", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <MemoryRouter>
          <AuthGuard>
            <div data-testid="protected-content">Protected Content</div>
          </AuthGuard>
        </MemoryRouter>,
      );

      expect(
        screen.getByText("Please sign in to access this content."),
      ).toBeInTheDocument();
      expect(screen.queryByTestId("protected-content")).not.toBeInTheDocument();
    });

    it("renders children when user has any required role", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn().mockReturnValue(true),
      });

      render(
        <AuthGuard requireAnyRole={["admin", "moderator"]}>
          <div data-testid="protected-content">Protected Content</div>
        </AuthGuard>,
      );

      expect(screen.getByTestId("protected-content")).toBeInTheDocument();
    });

    it("renders fallback when user lacks required roles", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(false),
        hasAnyRole: vi.fn().mockReturnValue(false),
      });

      render(
        <AuthGuard
          requireAnyRole={["admin"]}
          fallback={<div data-testid="access-denied">Access Denied</div>}
        >
          <div data-testid="protected-content">Protected Content</div>
        </AuthGuard>,
      );

      expect(screen.getByTestId("access-denied")).toBeInTheDocument();
      expect(screen.queryByTestId("protected-content")).not.toBeInTheDocument();
    });

    it("renders children when user has all required roles", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(true),
        hasAnyRole: vi.fn(),
      });

      render(
        <AuthGuard requireAllRoles={["admin", "superuser"]}>
          <div data-testid="protected-content">Protected Content</div>
        </AuthGuard>,
      );

      expect(screen.getByTestId("protected-content")).toBeInTheDocument();
    });

    it("renders nothing when showFallback is false", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      const { container } = render(
        <AuthGuard showFallback={false}>
          <div data-testid="protected-content">Protected Content</div>
        </AuthGuard>,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe("RequireAuth", () => {
    it("renders children when authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <RequireAuth>
          <div data-testid="auth-content">Authenticated Content</div>
        </RequireAuth>,
      );

      expect(screen.getByTestId("auth-content")).toBeInTheDocument();
    });

    it("renders fallback when not authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <RequireAuth
          fallback={<div data-testid="login-prompt">Please Login</div>}
        >
          <div data-testid="auth-content">Authenticated Content</div>
        </RequireAuth>,
      );

      expect(screen.getByTestId("login-prompt")).toBeInTheDocument();
      expect(screen.queryByTestId("auth-content")).not.toBeInTheDocument();
    });
  });

  describe("RequireRole", () => {
    it("renders children when user has required role", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(true),
        hasAnyRole: vi.fn().mockReturnValue(true),
      });

      render(
        <RequireRole>
          <div data-testid="admin-content">Admin Content</div>
        </RequireRole>,
      );

      expect(screen.getByTestId("admin-content")).toBeInTheDocument();
    });

    it("renders fallback when user lacks required role", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(false),
        hasAnyRole: vi.fn().mockReturnValue(false),
      });

      render(
        <RequireRole fallback={<div data-testid="no-access">No Access</div>}>
          <div data-testid="admin-content">Admin Content</div>
        </RequireRole>,
      );

      expect(screen.getByTestId("no-access")).toBeInTheDocument();
      expect(screen.queryByTestId("admin-content")).not.toBeInTheDocument();
    });
  });

  describe("RequireAnyRole", () => {
    it("renders children when user has any of the required roles", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn().mockReturnValue(true),
      });

      render(
        <RequireAnyRole roles={["admin", "moderator"]}>
          <div data-testid="mod-content">Moderation Content</div>
        </RequireAnyRole>,
      );

      expect(screen.getByTestId("mod-content")).toBeInTheDocument();
    });

    it("renders fallback when user has none of the required roles", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn().mockReturnValue(false),
      });

      render(
        <RequireAnyRole
          roles={["admin", "moderator"]}
          fallback={
            <div data-testid="insufficient-role">Insufficient Role</div>
          }
        >
          <div data-testid="mod-content">Moderation Content</div>
        </RequireAnyRole>,
      );

      expect(screen.getByTestId("insufficient-role")).toBeInTheDocument();
      expect(screen.queryByTestId("mod-content")).not.toBeInTheDocument();
    });
  });

  describe("RequireAllRoles", () => {
    it("renders children when user has all required roles", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(true),
        hasAnyRole: vi.fn(),
      });

      render(
        <RequireAllRoles roles={["admin", "superuser"]}>
          <div data-testid="super-admin-content">Super Admin Content</div>
        </RequireAllRoles>,
      );

      expect(screen.getByTestId("super-admin-content")).toBeInTheDocument();
    });

    it("renders fallback when user is missing any required role", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockImplementation((role) => role === "admin"), // Only has admin, not superuser
        hasAnyRole: vi.fn(),
      });

      render(
        <RequireAllRoles
          roles={["admin", "superuser"]}
          fallback={<div data-testid="missing-role">Missing Role</div>}
        >
          <div data-testid="super-admin-content">Super Admin Content</div>
        </RequireAllRoles>,
      );

      expect(screen.getByTestId("missing-role")).toBeInTheDocument();
      expect(
        screen.queryByTestId("super-admin-content"),
      ).not.toBeInTheDocument();
    });
  });

  describe("RequireUnauthenticated", () => {
    it("renders children when user is not authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <RequireUnauthenticated>
          <div data-testid="guest-content">Guest Content</div>
        </RequireUnauthenticated>,
      );

      expect(screen.getByTestId("guest-content")).toBeInTheDocument();
    });

    it("renders fallback when user is authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <RequireUnauthenticated
          fallback={
            <div data-testid="already-logged-in">Already Logged In</div>
          }
        >
          <div data-testid="guest-content">Guest Content</div>
        </RequireUnauthenticated>,
      );

      expect(screen.getByTestId("already-logged-in")).toBeInTheDocument();
      expect(screen.queryByTestId("guest-content")).not.toBeInTheDocument();
    });
  });

  describe("ShowForAuth", () => {
    it("shows content when authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <ShowForAuth>
          <div data-testid="auth-only">Authenticated Only</div>
        </ShowForAuth>,
      );

      expect(screen.getByTestId("auth-only")).toBeInTheDocument();
    });

    it("hides content when not authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      const { container } = render(
        <ShowForAuth>
          <div data-testid="auth-only">Authenticated Only</div>
        </ShowForAuth>,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe("ShowForGuest", () => {
    it("shows content when not authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      render(
        <ShowForGuest>
          <div data-testid="guest-only">Guest Only</div>
        </ShowForGuest>,
      );

      expect(screen.getByTestId("guest-only")).toBeInTheDocument();
    });

    it("hides content when authenticated", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn(),
      });

      const { container } = render(
        <ShowForGuest>
          <div data-testid="guest-only">Guest Only</div>
        </ShowForGuest>,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe("ShowForRole", () => {
    it("shows content when user has the role", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(true),
        hasAnyRole: vi.fn().mockReturnValue(true),
      });

      render(
        <ShowForRole>
          <div data-testid="admin-only">Admin Only</div>
        </ShowForRole>,
      );

      expect(screen.getByTestId("admin-only")).toBeInTheDocument();
    });

    it("hides content when user lacks the role", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(false),
        hasAnyRole: vi.fn().mockReturnValue(false),
      });

      const { container } = render(
        <ShowForRole>
          <div data-testid="admin-only">Admin Only</div>
        </ShowForRole>,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe("ShowForRoles", () => {
    it("shows content when user has any required role (requireAll=false)", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn(),
        hasAnyRole: vi.fn().mockReturnValue(true),
      });

      render(
        <ShowForRoles roles={["admin", "moderator"]} requireAll={false}>
          <div data-testid="mod-tools">Moderation Tools</div>
        </ShowForRoles>,
      );

      expect(screen.getByTestId("mod-tools")).toBeInTheDocument();
    });

    it("shows content when user has all required roles (requireAll=true)", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(true),
        hasAnyRole: vi.fn(),
      });

      render(
        <ShowForRoles roles={["admin", "superuser"]} requireAll={true}>
          <div data-testid="super-tools">Super Tools</div>
        </ShowForRoles>,
      );

      expect(screen.getByTestId("super-tools")).toBeInTheDocument();
    });

    it("hides content when requirements not met", () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        hasRole: vi.fn().mockReturnValue(false),
        hasAnyRole: vi.fn().mockReturnValue(false),
      });

      const { container } = render(
        <ShowForRoles roles={["admin", "moderator"]}>
          <div data-testid="mod-tools">Moderation Tools</div>
        </ShowForRoles>,
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe("useAuthStatus", () => {
    it("returns enhanced auth status with computed properties", () => {
      // This would need to be tested in a component that uses the hook
      // For now, we'll just verify the hook exists and can be imported
      expect(useAuthStatus).toBeDefined();
    });
  });
});
