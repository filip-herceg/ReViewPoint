import { ChevronRight, Home } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { findRouteByPath } from "@/lib/router/routes";

export function Breadcrumbs() {
	const location = useLocation();
	const pathSegments = location.pathname.split("/").filter(Boolean);

	// Don't show breadcrumbs on home page
	if (pathSegments.length === 0) {
		return null;
	}

	// Build breadcrumb items
	const breadcrumbItems = [{ path: "/", title: "Home", isHome: true }];

	let currentPath = "";
	for (const segment of pathSegments) {
		currentPath += `/${segment}`;
		const route = findRouteByPath(currentPath);

		if (route) {
			breadcrumbItems.push({
				path: currentPath,
				title: route.title,
				isHome: false,
			});
		} else {
			// If no route found, use the segment as title (capitalized)
			breadcrumbItems.push({
				path: currentPath,
				title: segment.charAt(0).toUpperCase() + segment.slice(1),
				isHome: false,
			});
		}
	}

	return (
		<nav
			className="flex items-center space-x-1 text-sm text-muted-foreground mb-4"
			aria-label="Breadcrumb"
		>
			<ol className="flex items-center space-x-1">
				{breadcrumbItems.map((item, index) => {
					const isLast = index === breadcrumbItems.length - 1;

					return (
						<li key={item.path} className="flex items-center">
							{index > 0 && (
								<ChevronRight className="h-4 w-4 text-border mx-1" />
							)}
							{isLast ? (
								<span className="text-foreground font-medium flex items-center">
									{item.isHome && <Home className="h-4 w-4 mr-1" />}
									{item.title}
								</span>
							) : (
								<Link
									to={item.path}
									className="text-info-foreground hover:text-info transition-colors flex items-center underline-offset-2 hover:underline"
								>
									{item.isHome && <Home className="h-4 w-4 mr-1" />}
									{item.title}
								</Link>
							)}
						</li>
					);
				})}
			</ol>
		</nav>
	);
}
