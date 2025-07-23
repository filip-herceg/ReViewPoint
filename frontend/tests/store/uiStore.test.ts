import { beforeEach, describe, expect, it } from "vitest";
import { useUIStore } from "@/lib/store/uiStore";

describe("uiStore error handling", () => {
	beforeEach(() => {
		useUIStore.setState({
			theme: "light",
			sidebarOpen: false,
			notifications: [],
		});
	});

	it("throws if setTheme called with invalid theme", () => {
		expect(() => useUIStore.getState().setTheme("blue" as never)).toThrow(
			/invalid theme/i,
		);
	});

	it("sets theme for valid values", () => {
		useUIStore.getState().setTheme("dark");
		expect(useUIStore.getState().theme).toBe("dark");
		useUIStore.getState().setTheme("light");
		expect(useUIStore.getState().theme).toBe("light");
	});

	it("toggles sidebar", () => {
		const prev = useUIStore.getState().sidebarOpen;
		useUIStore.getState().toggleSidebar();
		expect(useUIStore.getState().sidebarOpen).toBe(!prev);
	});

	it("throws if addNotification called with empty title", () => {
		expect(() =>
			useUIStore.getState().addNotification({
				type: "info",
				title: "",
			}),
		).toThrow(/notification title required/i);
	});

	it("adds notification for valid message", () => {
		const initialCount = useUIStore.getState().notifications.length;
		useUIStore.getState().addNotification({
			type: "info",
			title: "Hello",
		});
		expect(useUIStore.getState().notifications).toHaveLength(initialCount + 1);
		expect(useUIStore.getState().notifications[0].title).toBe("Hello");
	});

	it("throws if removeNotification called with invalid id", () => {
		expect(() => useUIStore.getState().removeNotification("")).toThrow(
			/invalid notification id/i,
		);
		expect(() =>
			useUIStore.getState().removeNotification("nonexistent"),
		).toThrow(/notification not found/i);
	});

	it("removes notification for valid id", () => {
		useUIStore.getState().addNotification({ type: "info", title: "A" });
		useUIStore.getState().addNotification({ type: "info", title: "B" });

		const notifications = useUIStore.getState().notifications;
		expect(notifications).toHaveLength(2);

		const firstId = notifications[0].id;
		useUIStore.getState().removeNotification(firstId);

		const remainingNotifications = useUIStore.getState().notifications;
		expect(remainingNotifications).toHaveLength(1);
		expect(remainingNotifications[0].title).toBe("B");
	});
});
