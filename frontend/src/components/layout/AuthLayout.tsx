import type React from "react";
import { Link } from "react-router-dom";
import { WebSocketStatus } from "@/components/websocket/WebSocketStatus";

interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-muted flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <Link to="/" className="inline-block">
            <h1 className="text-3xl font-bold text-foreground">ReViewPoint</h1>
          </Link>
          <p className="mt-2 text-sm text-muted-foreground">
            PDF Review and Analysis Platform
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-background py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {children}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-sm text-muted-foreground">
          <Link
            to="/"
            className="text-info-foreground hover:text-info underline"
          >
            ← Back to Home
          </Link>
        </p>
        <div className="mt-4 flex justify-center">
          <WebSocketStatus inline />
        </div>
      </div>
    </div>
  );
}
