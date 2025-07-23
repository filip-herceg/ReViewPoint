import { beforeEach, describe, expect, it } from "vitest";
import { useUIStore } from "../uiStore";

const resetUIStore = () => {
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
    const state = useUIStore.getState();
    expect(state.theme).toBe("light");
    expect(state.sidebarOpen).toBe(false);
    expect(state.notifications).toEqual([]);
  });

  it("should set theme", () => {
    useUIStore.getState().setTheme("dark");
    expect(useUIStore.getState().theme).toBe("dark");
    useUIStore.getState().setTheme("light");
    expect(useUIStore.getState().theme).toBe("light");
  });

  it("should toggle sidebar", () => {
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(true);
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it("should add and remove notifications", () => {
    useUIStore.getState().addNotification("Test 1");
    useUIStore.getState().addNotification("Test 2");
    expect(useUIStore.getState().notifications).toEqual(["Test 1", "Test 2"]);
    useUIStore.getState().removeNotification(0);
    expect(useUIStore.getState().notifications).toEqual(["Test 2"]);
  });
});
