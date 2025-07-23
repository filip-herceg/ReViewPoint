import * as Icons from "lucide-react";
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { WebSocketSidebarDebug } from "@/components/debug/WebSocketSidebarDebug";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { routes } from "@/lib/router/routes";
import { cn } from "@/lib/utils";

const iconMap: Record<
  string,
  React.ComponentType<React.SVGProps<SVGSVGElement>>
> = {
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
  FileDigit: Icons.FileDigit,
  ChevronRight: Icons.ChevronRight,
  ChevronDown: Icons.ChevronDown,
};

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export function Sidebar({ sidebarOpen, setSidebarOpen }: SidebarProps) {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();

  // Find the current main route and its children
  const getCurrentRouteData = () => {
    const currentPath = location.pathname;

    // Find the main route that matches current path
    const mainRoute = routes.find((route) => {
      if (route.path === "/" && currentPath === "/") return true;
      if (route.path !== "/" && currentPath.startsWith(route.path)) return true;
      return false;
    });

    return {
      mainRoute,
      subRoutes: mainRoute?.children || [],
      currentPath,
    };
  };

  const { mainRoute, subRoutes, currentPath } = getCurrentRouteData();

  const _toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Sidebar - Only shown when expanded */}
      {sidebarOpen && (
        <aside
          id="sidebar"
          className="flex flex-col bg-background/95 backdrop-blur-md border-r border-border shadow-xl fixed top-16 left-0 h-[calc(100vh-4rem)] w-64 z-40"
        >
          {/* Current Page Info */}
          {mainRoute && (
            <div className="p-4 border-b border-border">
              <div className="flex items-center space-x-3">
                {mainRoute.icon &&
                  iconMap[mainRoute.icon] &&
                  React.createElement(iconMap[mainRoute.icon], {
                    className: "h-5 w-5 text-primary",
                  })}
                <div>
                  <h3 className="font-semibold text-sm">{mainRoute.title}</h3>
                  <p className="text-xs text-muted-foreground">
                    {mainRoute.description}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Content */}
          <nav className="flex-1 p-4 space-y-3">
            <div className="space-y-3">
              {mainRoute && (
                <Link
                  to={mainRoute.path}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:bg-accent",
                    currentPath === mainRoute.path
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  <Icons.Home className="h-4 w-4 mr-2" />
                  Overview
                </Link>
              )}

              {subRoutes.length > 0 && (
                <>
                  <div className="px-3 py-1">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Pages
                    </h4>
                  </div>
                  {subRoutes.map((subRoute) => {
                    const isActive =
                      currentPath === subRoute.path ||
                      (subRoute.path !== "/" &&
                        currentPath.startsWith(subRoute.path));

                    return (
                      <Link
                        key={subRoute.path}
                        to={subRoute.path}
                        className={cn(
                          "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:bg-accent",
                          isActive
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:text-foreground",
                        )}
                      >
                        <Icons.ChevronRight className="h-4 w-4 mr-2" />
                        {subRoute.title}
                      </Link>
                    );
                  })}
                </>
              )}

              {/* Quick actions based on current page */}
              {mainRoute?.path === "/uploads" && (
                <>
                  <div className="px-3 py-1 mt-6">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Quick Actions
                    </h4>
                  </div>
                  <Link
                    to="/uploads/new"
                    className="flex items-center px-3 py-2 rounded-lg text-sm font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-all duration-200"
                  >
                    <Icons.Plus className="h-4 w-4 mr-2" />
                    New Upload
                  </Link>
                </>
              )}

              {mainRoute?.path === "/marketplace" && (
                <>
                  <div className="px-3 py-1 mt-6">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Quick Actions
                    </h4>
                  </div>
                  <Link
                    to="/my-modules"
                    className="flex items-center px-3 py-2 rounded-lg text-sm font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-all duration-200"
                  >
                    <Icons.Package className="h-4 w-4 mr-2" />
                    My Modules
                  </Link>
                </>
              )}

              {/* WebSocket Debug for Home page */}
              {mainRoute?.path === "/" && (
                <div className="mt-6">
                  <WebSocketSidebarDebug />
                </div>
              )}
            </div>
          </nav>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center space-x-3 p-3 rounded-xl bg-accent hover:bg-accent/80 transition-colors">
              <div className="p-2 bg-gradient-to-br from-primary to-primary/80 rounded-lg">
                <Icons.User className="h-4 w-4 text-primary-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {user?.name || user?.email}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user?.email}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={logout}
                aria-label="Logout"
                className="hover:bg-destructive hover:text-destructive-foreground transition-colors"
              >
                <Icons.LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </aside>
      )}
    </>
  );
}
