import * as Icons from "lucide-react";
import type React from "react";
import { Link, useLocation } from "react-router-dom";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/useAuth";
import { getRoleBasedNavigationRoutes } from "@/lib/router/routes";
import { cn } from "@/lib/utils";

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

export function Navigation() {
	const location = useLocation();
	const { isAuthenticated, user, logout } = useAuth();
	const userRoles = user?.roles || [];
	const navigationRoutes = getRoleBasedNavigationRoutes(userRoles);

	// Filter out Home when authenticated, and Profile since it's now in the dropdown
	const filteredRoutes = navigationRoutes.filter((route) => {
		if (isAuthenticated && route.path === "/") return false; // Remove Home when logged in
		if (route.path === "/profile") return false; // Profile is now in dropdown
		if (route.path === "/file-dashboard-test") return false; // Move to settings
		return true;
	});

	return (
		<nav className="flex items-center space-x-4">
			{/* Main Navigation Links */}
			<div className="hidden md:flex space-x-1">
				{filteredRoutes.map((route) => {
					// Only show authenticated routes if user is logged in
					if (route.requiresAuth && !isAuthenticated) {
						return null;
					}

					const Icon = route.icon ? iconMap[route.icon] : null;
					const isActive =
						location.pathname === route.path ||
						(route.path !== "/" && location.pathname.startsWith(route.path));

					return (
						<Link
							key={route.path}
							to={route.path}
							className={cn(
								"flex items-center px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group hover:scale-105",
								isActive
									? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
									: "text-muted-foreground hover:text-foreground hover:bg-accent/50 hover:shadow-md",
							)}
						>
							{Icon && (
								<Icon
									className={cn(
										"h-5 w-5 mr-3 transition-transform duration-200",
										isActive
											? "text-primary-foreground"
											: "text-muted-foreground group-hover:text-foreground group-hover:scale-110",
									)}
								/>
							)}
							{route.title}
						</Link>
					);
				})}
			</div>

			{/* User Menu */}
			{isAuthenticated ? (
				<DropdownMenu>
					<DropdownMenuTrigger asChild>
						<button className="flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-all duration-200 hover:scale-105">
							<Icons.User className="h-4 w-4" />
							<span className="hidden sm:block">
								{user?.name || user?.email}
							</span>
							<Icons.ChevronDown className="h-4 w-4" />
						</button>
					</DropdownMenuTrigger>
					<DropdownMenuContent align="end" className="w-56">
						<DropdownMenuLabel>
							<div className="flex flex-col space-y-1">
								<p className="text-sm font-medium leading-none">
									{user?.name || "User"}
								</p>
								<p className="text-xs leading-none text-muted-foreground">
									{user?.email}
								</p>
							</div>
						</DropdownMenuLabel>
						<DropdownMenuSeparator />
						<DropdownMenuItem asChild>
							<Link to="/profile" className="flex items-center">
								<Icons.User className="mr-2 h-4 w-4" />
								<span>Profile</span>
							</Link>
						</DropdownMenuItem>
						<DropdownMenuItem asChild>
							<Link to="/settings" className="flex items-center">
								<Icons.Settings className="mr-2 h-4 w-4" />
								<span>Settings</span>
							</Link>
						</DropdownMenuItem>
						<DropdownMenuSeparator />
						<DropdownMenuItem
							onClick={logout}
							className="text-destructive focus:text-destructive"
						>
							<Icons.LogOut className="mr-2 h-4 w-4" />
							<span>Logout</span>
						</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>
			) : (
				<div className="flex items-center space-x-2">
					<Link
						to="/auth/login"
						className="px-3 py-2 text-sm font-medium text-info-foreground hover:text-info hover:bg-accent/70 rounded-xl transition-all duration-200 hover:scale-105 underline-offset-2 hover:underline"
					>
						Login
					</Link>
					<Link
						to="/auth/register"
						className="px-3 py-2 text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 rounded-xl transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-primary/25"
					>
						Register
					</Link>
				</div>
			)}
		</nav>
	);
}
