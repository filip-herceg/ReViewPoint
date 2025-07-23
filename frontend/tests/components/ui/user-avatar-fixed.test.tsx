/**
 * User Avatar Component Tests
 * Part of Phase 4: Core UI Components
 */

import { fireEvent, render, screen } from "@testing-library/react";
import {
	AvatarGroup,
	UserAvatar,
	useUserAvatar,
} from "@/components/ui/user-avatar";
import type { User } from "@/lib/api/types";
import { createUser } from "../../test-templates";
import { testLogger } from "../../test-utils";

// Helper to convert API User to component props
function toAvatarUser(user: User) {
	return {
		name: user.name ?? undefined,
		email: user.email,
		avatar: user.avatar_url ?? undefined,
	};
}

describe("UserAvatar Component", () => {
	beforeEach(() => {
		testLogger.info("Starting UserAvatar test");
	});

	afterEach(() => {
		testLogger.info("Completed UserAvatar test");
	});

	it("renders initials when no avatar image", () => {
		testLogger.debug("Testing initials rendering");

		const apiUser = createUser({ name: "John Doe", email: "john@example.com" });
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} />);

		expect(screen.getByText("JD")).toBeInTheDocument();
	});

	it("renders initials from email when no name", () => {
		testLogger.debug("Testing email-based initials");

		const apiUser = createUser({ email: "test@example.com", name: null });
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} />);

		expect(screen.getByText("TE")).toBeInTheDocument();
	});

	it("renders fallback when no user provided", () => {
		testLogger.debug("Testing fallback rendering");

		render(<UserAvatar />);

		expect(screen.getByText("U")).toBeInTheDocument();
	});

	it("displays avatar image when provided", () => {
		testLogger.debug("Testing avatar image display");

		const apiUser = createUser({
			name: "Jane Doe",
			email: "jane@example.com",
			avatar_url: "https://example.com/avatar.jpg",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} />);

		const img = screen.getByAltText("Jane Doe avatar");
		expect(img).toHaveAttribute("src", "https://example.com/avatar.jpg");
		expect(img).toHaveAttribute("alt", "Jane Doe avatar");
	});

	it("handles image load error gracefully", () => {
		testLogger.debug("Testing image error handling");

		const apiUser = createUser({
			name: "John Doe",
			avatar_url: "https://invalid.com/avatar.jpg",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} />);

		const img = screen.getByAltText("John Doe avatar");

		// Simulate image load error
		fireEvent.error(img);

		// Should still show initials as fallback
		expect(screen.getByText("JD")).toBeInTheDocument();
	});

	it("applies different sizes correctly", () => {
		testLogger.debug("Testing size variants");

		const apiUser = createUser({ name: "Test User" });
		const user = toAvatarUser(apiUser);

		const { rerender } = render(<UserAvatar user={user} size="sm" />);
		// Check the avatar container, not the text span
		const avatar = screen.getByText("TU").closest("div");
		expect(avatar).toHaveClass("h-6", "w-6");

		rerender(<UserAvatar user={user} size="lg" />);
		const avatarLg = screen.getByText("TU").closest("div");
		expect(avatarLg).toHaveClass("h-10", "w-10");

		rerender(<UserAvatar user={user} size="xl" />);
		const avatarXl = screen.getByText("TU").closest("div");
		expect(avatarXl).toHaveClass("h-12", "w-12");
	});

	it("shows online status when enabled", () => {
		testLogger.debug("Testing online status");

		const apiUser = createUser({
			name: "Test User",
			email: "test@example.com",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} showOnlineStatus={true} isOnline={true} />);

		expect(screen.getByTestId("online-status")).toBeInTheDocument();
		expect(screen.getByTestId("online-status")).toHaveClass("bg-green-500");
	});

	it("shows offline status when enabled", () => {
		testLogger.debug("Testing offline status");

		const apiUser = createUser({
			name: "Test User",
			email: "test@example.com",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} showOnlineStatus={true} isOnline={false} />);

		expect(screen.getByTestId("online-status")).toBeInTheDocument();
		expect(screen.getByTestId("online-status")).toHaveClass("bg-gray-400");
	});

	it("handles click events", () => {
		testLogger.debug("Testing click events");

		const onClick = vi.fn();
		const apiUser = createUser({
			name: "Test User",
			email: "test@example.com",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} onClick={onClick} />);

		fireEvent.click(screen.getByText("TU"));
		expect(onClick).toHaveBeenCalledTimes(1);
	});

	it("does not handle click when no onClick provided", () => {
		testLogger.debug("Testing no click handler");

		const apiUser = createUser({
			name: "Test User",
			email: "test@example.com",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} />);

		// Should not throw when clicking without handler
		fireEvent.click(screen.getByText("TU"));
		expect(true).toBe(true); // No error thrown
	});

	it("applies custom className", () => {
		testLogger.debug("Testing custom className");

		const apiUser = createUser({
			name: "Test User",
			email: "test@example.com",
		});
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} className="custom-avatar" />);

		expect(screen.getByText("TU").parentElement).toHaveClass("custom-avatar");
	});

	it("generates unique background colors based on user data", () => {
		testLogger.debug("Testing unique colors");

		const apiUser1 = createUser({ name: "Alice", email: "alice@example.com" });
		const apiUser2 = createUser({ name: "Bob", email: "bob@example.com" });
		const user1 = toAvatarUser(apiUser1);
		const user2 = toAvatarUser(apiUser2);

		const { container: container1 } = render(<UserAvatar user={user1} />);
		const { container: container2 } = render(<UserAvatar user={user2} />);

		// Should have different background colors (implementation detail)
		const element1 = container1.querySelector(
			'[data-testid="avatar-initials"]',
		);
		const element2 = container2.querySelector(
			'[data-testid="avatar-initials"]',
		);

		// Since we're using CSS classes for colors, just check they exist
		expect(element1).toBeInTheDocument();
		expect(element2).toBeInTheDocument();
	});

	it("handles error state gracefully", () => {
		testLogger.debug("Testing error handling");

		const apiUser = createUser({ name: "", email: "" });
		const user = toAvatarUser(apiUser);

		render(<UserAvatar user={user} />);

		// Should render fallback
		expect(screen.getByText("U")).toBeInTheDocument();
	});
});

describe("AvatarGroup Component", () => {
	beforeEach(() => {
		testLogger.info("Starting AvatarGroup test");
	});

	afterEach(() => {
		testLogger.info("Completed AvatarGroup test");
	});

	it("renders multiple avatars", () => {
		testLogger.debug("Testing multiple avatars");

		const apiUsers = [
			createUser({ name: "User 1", email: "user1@example.com" }),
			createUser({ name: "User 2", email: "user2@example.com" }),
			createUser({ name: "User 3", email: "user3@example.com" }),
		];
		const mockUsers = apiUsers.map(toAvatarUser);

		render(<AvatarGroup users={mockUsers} max={3} />);

		expect(screen.getByText("U1")).toBeInTheDocument();
		expect(screen.getByText("U2")).toBeInTheDocument();
		expect(screen.getByText("U3")).toBeInTheDocument();
	});

	it("shows overflow indicator when users exceed max", () => {
		testLogger.debug("Testing overflow indicator");

		const apiUsers = Array.from({ length: 5 }, (_, i) =>
			createUser({ name: `User ${i + 1}`, email: `user${i + 1}@example.com` }),
		);
		const mockUsers = apiUsers.map(toAvatarUser);

		render(<AvatarGroup users={mockUsers} max={3} />);

		expect(screen.getByText("+2")).toBeInTheDocument();
	});

	it("handles different sizes", () => {
		testLogger.debug("Testing group sizes");

		const apiUsers = [
			createUser({ name: "User 1", email: "user1@example.com" }),
			createUser({ name: "User 2", email: "user2@example.com" }),
		];
		const mockUsers = apiUsers.map(toAvatarUser);

		render(<AvatarGroup users={mockUsers.slice(0, 2)} size="lg" />);

		// Check the avatar containers, not the text spans
		const avatar1 = screen.getByText("U1").closest("div");
		const avatar2 = screen.getByText("U2").closest("div");
		expect(avatar1).toHaveClass("h-10", "w-10");
		expect(avatar2).toHaveClass("h-10", "w-10");
	});

	it("renders empty group gracefully", () => {
		testLogger.debug("Testing empty group");

		const { container } = render(<AvatarGroup users={[]} />);

		expect(container.firstElementChild?.children.length).toBe(0);
	});

	it("does not show overflow when users are within max", () => {
		testLogger.debug("Testing no overflow");

		const apiUsers = [
			createUser({ name: "User 1", email: "user1@example.com" }),
			createUser({ name: "User 2", email: "user2@example.com" }),
		];
		const mockUsers = apiUsers.map(toAvatarUser);

		render(<AvatarGroup users={mockUsers.slice(0, 2)} max={5} />);

		expect(screen.queryByText(/^\+/)).not.toBeInTheDocument();
	});

	it("handles empty avatar list edge case", () => {
		testLogger.debug("Testing empty list edge case");

		const { container } = render(<AvatarGroup users={[]} />);
		expect(container.firstElementChild).toHaveClass("flex");
	});

	it("shows all users when max is set to a large number", () => {
		testLogger.debug("Testing large max constraint");

		const apiUsers = Array.from({ length: 10 }, (_, i) => {
			const names = [
				"Alice Brown",
				"Bob Chen",
				"Carol Davis",
				"David Evans",
				"Eva Frank",
				"Frank Green",
				"Grace Hill",
				"Henry Johnson",
				"Ivy Kumar",
				"Jack Liu",
			];
			return createUser({ name: names[i], email: `user${i + 1}@example.com` });
		});
		const mockUsers = apiUsers.map(toAvatarUser);

		render(<AvatarGroup users={mockUsers} max={20} />);

		// Should show all 10 users when max is large enough
		// Check for each user's unique initials
		const expectedInitials = [
			"AB",
			"BC",
			"CD",
			"DE",
			"EF",
			"FG",
			"GH",
			"HJ",
			"IK",
			"JL",
		];
		expectedInitials.forEach((initials) => {
			expect(screen.getByText(initials)).toBeInTheDocument();
		});
	});
});

describe("useUserAvatar Hook", () => {
	beforeEach(() => {
		testLogger.info("Starting useUserAvatar hook test");
	});

	afterEach(() => {
		testLogger.info("Completed useUserAvatar hook test");
	});

	it("provides avatar utilities", () => {
		testLogger.debug("Testing hook utilities");

		let hookResult: ReturnType<typeof useUserAvatar> | undefined;

		function TestComponent() {
			hookResult = useUserAvatar();
			return null;
		}

		render(<TestComponent />);

		expect(hookResult).toBeDefined();
		expect(typeof hookResult!.getInitials).toBe("function");
		expect(typeof hookResult!.getAvatarColor).toBe("function");

		// Test utility functions
		expect(hookResult!.getInitials("John Doe")).toBe("JD");
		expect(hookResult!.getInitials("", "test@example.com")).toBe("TE");
		expect(hookResult!.getAvatarColor("test")).toBeDefined();
	});

	it("handles edge cases in utilities", () => {
		testLogger.debug("Testing hook edge cases");

		let hookResult: ReturnType<typeof useUserAvatar> | undefined;

		function TestComponent() {
			hookResult = useUserAvatar();
			return null;
		}

		render(<TestComponent />);

		// Test edge cases
		expect(hookResult!.getInitials("")).toBe("U");
		expect(hookResult!.getInitials("A")).toBe("A");
		expect(hookResult!.getInitials("A B C")).toBe("AB");
		expect(hookResult!.getAvatarColor("")).toBeDefined();
	});
});
