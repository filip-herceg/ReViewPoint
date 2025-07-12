/**
 * Enhanced AppShell Component with Sidebar
 * Responsive layout with collapsible sidebar
 * Part of Phase 4: Core UI Components
 */

import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Navigation } from "@/components/navigation/Navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { Breadcrumbs } from "@/components/navigation/Breadcrumbs";
import { WebSocketStatus } from "@/components/websocket/WebSocketStatus";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { SkipLinks } from "@/components/ui/skip-links";
import { useAuth } from "@/hooks/useAuth";
import { useUIStore } from "@/lib/store/uiStore";
import { ErrorBoundary } from "react-error-boundary";
import { getErrorMessage } from "@/lib/utils/errorHandling";
import logger from "@/logger";
import * as Icons from "lucide-react";
import logoSymbol from "@/assets/logos/Logo_symbol_color.svg";
import logoText from "@/assets/logos/Logo_text1_color.svg";

const iconMap: Record<string, React.ComponentType<any>> = {
  Home: Icons.Home,
  LayoutDashboard: Icons.LayoutDashboard,
  Upload: Icons.Upload,
  FileText: Icons.FileText,
  User: Icons.User,
  Settings: Icons.Settings,
  Shield: Icons.Shield,
  UserCheck: Icons.UserCheck,
  Store: Icons.Store,
  Package: Icons.Package,
};

function ErrorFallback({ error }: { error: unknown }) {
  return (
    <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
      <h2 className="text-lg font-semibold text-destructive mb-2">
        Something went wrong
      </h2>
      <p className="text-destructive mb-4">{getErrorMessage(error)}</p>
      <Button onClick={() => window.location.reload()} variant="destructive">
        Reload page
      </Button>
    </div>
  );
}

interface AppShellProps {
  children: React.ReactNode;
}

/**
 * Enhanced AppShell with Sidebar
 * Provides responsive layout with collapsible sidebar navigation
 */
export function AppShell({ children }: AppShellProps) {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const { sidebarOpen, setSidebarOpen } = useUIStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
    logger.info("AppShell: Mobile menu toggled", {
      mobileMenuOpen: !mobileMenuOpen,
    });
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-accent/10">
      {/* Skip Links for Accessibility */}
      <SkipLinks />

      {/* Header */}
      <header
        id="header"
        className="bg-background/95 backdrop-blur-md shadow-sm border-b border-border/50 fixed top-0 left-0 right-0 z-50" // Increase z-index for dominance
      >
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Sidebar Toggle Button - Top Level */}
            {isAuthenticated && (
              <Button
                variant="ghost"
                size="default"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="hover:bg-accent p-2"
                aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
              >
                <Icons.PanelLeftClose
                  className={cn(
                    "h-6 w-6 transition-transform duration-300",
                    !sidebarOpen && "rotate-180",
                  )}
                />
              </Button>
            )}

            {/* Center Section - Logo */}
            <div className="flex items-center space-x-3">
              {/* Mobile Menu Button */}
              {isAuthenticated && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="md:hidden hover:bg-accent"
                  aria-label="Toggle sidebar"
                >
                  <Icons.Menu className="h-5 w-5" />
                </Button>
              )}

              {/* Logo */}
              <Link
                to={isAuthenticated ? "/dashboard" : "/"}
                className="flex items-center space-x-2 group h-11"
              >
                <img
                  src={logoSymbol}
                  alt="Logo Symbol"
                  className="h-full w-auto"
                />
                <img src={logoText} alt="Logo Text" className="h-full w-auto" />
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:block">
              <Navigation />
            </div>

            {/* Header Actions */}
            <div className="flex items-center space-x-2">
              <ThemeToggle variant="icon" />
              <WebSocketStatus inline />

              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleMobileMenu}
                className="md:hidden hover:bg-accent"
                aria-label="Toggle mobile menu"
              >
                <Icons.MoreVertical className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border/50 bg-background/95 backdrop-blur-md">
            <div className="px-4 py-3 space-y-1">
              <Navigation />
            </div>
          </div>
        )}
      </header>

      {/* Layout Container */}
      <div className="flex pt-16">
        {/* Sidebar */}
        {isAuthenticated && (
          <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        )}

        {/* Main Content */}
        <main
          id="main-content"
          className={cn(
            "flex-1 transition-all duration-200",
            isAuthenticated && sidebarOpen ? "ml-64" : "ml-0", // Only add margin when sidebar is open
          )}
        >
          <div className="px-4 sm:px-6 lg:px-8 py-6">
            {/* Breadcrumbs */}
            <Breadcrumbs />

            {/* Page Content */}
            <ErrorBoundary FallbackComponent={ErrorFallback}>
              {children}
            </ErrorBoundary>
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer
        id="footer"
        className="bg-background/95 backdrop-blur-md border-t border-border/50 mt-12"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              © 2025 ReViewPoint. All rights reserved.
            </p>
            <WebSocketStatus showDetails />
          </div>
        </div>
      </footer>
    </div>
  );
}
