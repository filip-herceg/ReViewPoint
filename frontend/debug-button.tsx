import React from "react";
import { BrowserRouter, Link } from "react-router-dom";
import { Button } from "./src/components/ui/button";

// Simple test to debug the issue
function DebugButton() {
  console.log("DebugButton: Starting test");

  return (
    <BrowserRouter>
      <div>
        <h1>Debug Button Test</h1>

        {/* This should work - single child */}
        <Button asChild>
          <Link to="/test">Navigate</Link>
        </Button>

        {/* This will fail - multiple children */}
        <Button asChild>
          <Link to="/test">
            Navigate
            <span>Icon</span>
          </Link>
        </Button>
      </div>
    </BrowserRouter>
  );
}

export default DebugButton;
