import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter, Link } from "react-router-dom";
import { Button } from "../src/components/ui/button";
import { it, expect } from "vitest";

// Quick debug test
it("debug button asChild", () => {
  console.log("=== DEBUG TEST START ===");

  // Test WITHOUT asChild first
  const { container: container1 } = render(
    <BrowserRouter>
      <Button>Standard Button</Button>
    </BrowserRouter>,
  );

  console.log("Standard Button HTML:", container1.innerHTML);

  // Test WITH asChild but no BrowserRouter (simpler)
  const { container: container2 } = render(
    <Button asChild>
      <a href="/test">Navigate</a>
    </Button>,
  );

  console.log("asChild Button HTML:", container2.innerHTML);

  console.log("=== DEBUG TEST END ===");
});
