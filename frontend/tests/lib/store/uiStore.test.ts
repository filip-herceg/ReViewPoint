import { describe, it, expect, beforeEach } from "vitest";
import { useUIStore } from "@/lib/store/uiStore";
import { testLogger } from "../../test-utils";

const resetUIStore = () => {
  testLogger.info("Resetting UI store state");
  useUIStore.setState({
    theme: "light",
    sidebarOpen: false,
    notifications: [],
  });
};

describe("uiStore", () => {
  beforeEach(() => {
    resetUIStore();
  });

  it("should have initial state", () => {
    testLogger.info("Checking initial UI store state");
    const state = useUIStore.getState();
    testLogger.debug("Initial state", state);
    expect(state.theme).toBe("light");
    expect(state.sidebarOpen).toBe(false);
    expect(state.notifications).toEqual([]);
  });

  it("should set theme", () => {
    testLogger.info("Testing setTheme");
    useUIStore.getState().setTheme("dark");
    testLogger.debug(
      'Theme after setTheme("dark")',
      useUIStore.getState().theme,
    );
    expect(useUIStore.getState().theme).toBe("dark");
    useUIStore.getState().setTheme("light");
    testLogger.debug(
      'Theme after setTheme("light")',
      useUIStore.getState().theme,
    );
    expect(useUIStore.getState().theme).toBe("light");
  });

  it("should toggle sidebar", () => {
    testLogger.info("Testing toggleSidebar");
    useUIStore.getState().toggleSidebar();
    testLogger.debug(
      "Sidebar open after first toggle",
      useUIStore.getState().sidebarOpen,
    );
    expect(useUIStore.getState().sidebarOpen).toBe(true);
    useUIStore.getState().toggleSidebar();
    testLogger.debug(
      "Sidebar open after second toggle",
      useUIStore.getState().sidebarOpen,
    );
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it("should add and remove notifications", () => {
    testLogger.info("Testing addNotification and removeNotification");

    // Add notifications with proper object format
    useUIStore.getState().addNotification({ type: "info", title: "Test 1" });
    useUIStore.getState().addNotification({ type: "info", title: "Test 2" });

    testLogger.debug(
      "Notifications after adding",
      useUIStore.getState().notifications,
    );
    expect(useUIStore.getState().notifications).toHaveLength(2);
    expect(useUIStore.getState().notifications[0].title).toBe("Test 1");
    expect(useUIStore.getState().notifications[1].title).toBe("Test 2");

    // Remove notification by ID
    const firstNotificationId = useUIStore.getState().notifications[0].id;
    useUIStore.getState().removeNotification(firstNotificationId);

    testLogger.debug(
      "Notifications after removing first",
      useUIStore.getState().notifications,
    );
    expect(useUIStore.getState().notifications).toHaveLength(1);
    expect(useUIStore.getState().notifications[0].title).toBe("Test 2");
  });
});
