# auth.ts - Authentication API Module

## Purpose

The `auth.ts` file provides comprehensive authentication and authorization functionality for the ReViewPoint application. This module serves as the primary interface between the frontend and backend authentication services, offering secure user registration, login, logout, token management, and password reset capabilities. It mirrors the backend authentication endpoints while providing a consistent TypeScript interface with robust error handling and security features.

## Key Features

### Core Authentication Operations

- **User Registration**: Secure account creation with validation
- **User Login**: Credential-based authentication with JWT tokens
- **User Logout**: Secure session termination and token invalidation
- **Token Management**: Automatic token refresh and session maintenance
- **Password Recovery**: Complete password reset workflow with email verification

### Security Features

- **JWT Token-Based Authentication**: Secure, stateless authentication
- **Automatic Token Refresh**: Seamless session extension without user intervention
- **Secure Password Handling**: Client-side validation and secure transmission
- **Session Management**: Complete session lifecycle management
- **Error Handling**: Comprehensive error handling with detailed logging

## API Functions

### User Registration (`register`)

Creates a new user account with comprehensive validation and security features.

```typescript
async function register(
  userData: AuthRegisterRequest,
): Promise<AuthRegisterResponse>;
```

**Parameters:**

- `userData: AuthRegisterRequest` - User registration data including email, name, and password

**Returns:**

- `Promise<AuthRegisterResponse>` - Registration response with user data and authentication tokens

**Example Usage:**

```typescript
import { authApi } from "@/lib/api";

async function handleUserRegistration() {
  try {
    const userData = {
      email: "john.doe@example.com",
      name: "John Doe",
      password: "SecurePassword123!",
    };

    const response = await authApi.register(userData);

    console.log("Registration successful:", {
      user: response.user,
      hasToken: !!response.access_token,
    });

    // Store authentication tokens
    localStorage.setItem("access_token", response.access_token);
    localStorage.setItem("refresh_token", response.refresh_token);
    localStorage.setItem("token_type", response.token_type);

    // Redirect to dashboard or main application
    window.location.href = "/dashboard";

    return response;
  } catch (error) {
    console.error("Registration failed:", error.message);

    // Handle specific registration errors
    if (error.message.includes("email already exists")) {
      showError(
        "This email is already registered. Please use a different email or try logging in.",
      );
    } else if (error.message.includes("password")) {
      showError(
        "Password does not meet security requirements. Please choose a stronger password.",
      );
    } else if (error.message.includes("validation")) {
      showError("Please check your input and try again.");
    } else {
      showError("Registration failed. Please try again later.");
    }

    throw error;
  }
}

// Registration with validation
async function registrationWithValidation(formData: {
  email: string;
  name: string;
  password: string;
  confirmPassword: string;
}) {
  // Client-side validation
  const errors = validateRegistrationData(formData);
  if (errors.length > 0) {
    throw new Error(`Validation failed: ${errors.join(", ")}`);
  }

  // Prepare registration data
  const userData = {
    email: formData.email.toLowerCase().trim(),
    name: formData.name.trim(),
    password: formData.password,
  };

  return await authApi.register(userData);
}

function validateRegistrationData(data: {
  email: string;
  name: string;
  password: string;
  confirmPassword: string;
}): string[] {
  const errors: string[] = [];

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    errors.push("Please enter a valid email address");
  }

  // Name validation
  if (data.name.length < 2) {
    errors.push("Name must be at least 2 characters long");
  }

  // Password validation
  if (data.password.length < 8) {
    errors.push("Password must be at least 8 characters long");
  }
  if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
    errors.push("Password must contain uppercase, lowercase, and number");
  }

  // Confirm password
  if (data.password !== data.confirmPassword) {
    errors.push("Passwords do not match");
  }

  return errors;
}
```

### User Authentication (`login`)

Authenticates existing users and establishes secure sessions.

```typescript
async function login(loginData: AuthLoginRequest): Promise<AuthLoginResponse>;
```

**Parameters:**

- `loginData: AuthLoginRequest` - Login credentials (email and password)

**Returns:**

- `Promise<AuthLoginResponse>` - Authentication response with user data and tokens

**Example Usage:**

```typescript
async function handleUserLogin() {
  try {
    const credentials = {
      email: "john.doe@example.com",
      password: "SecurePassword123!",
    };

    const response = await authApi.login(credentials);

    console.log("Login successful:", {
      user: response.user,
      tokenType: response.token_type,
    });

    // Store authentication data
    storeAuthenticationData(response);

    // Update application state
    updateUserSession(response.user);

    // Redirect to intended destination
    const returnUrl = sessionStorage.getItem("returnUrl") || "/dashboard";
    sessionStorage.removeItem("returnUrl");
    window.location.href = returnUrl;

    return response;
  } catch (error) {
    console.error("Login failed:", error.message);

    handleLoginError(error);
    throw error;
  }
}

function storeAuthenticationData(authResponse: AuthLoginResponse) {
  // Store tokens securely
  localStorage.setItem("access_token", authResponse.access_token);
  localStorage.setItem("refresh_token", authResponse.refresh_token);
  localStorage.setItem("token_type", authResponse.token_type);

  // Store user data (excluding sensitive info)
  const userData = {
    id: authResponse.user.id,
    email: authResponse.user.email,
    name: authResponse.user.name,
    role: authResponse.user.role,
  };
  localStorage.setItem("user_data", JSON.stringify(userData));

  // Set session timestamp
  localStorage.setItem("login_timestamp", new Date().toISOString());
}

function handleLoginError(error: Error) {
  if (error.message.includes("invalid credentials")) {
    showError(
      "Invalid email or password. Please check your credentials and try again.",
    );
  } else if (error.message.includes("account locked")) {
    showError(
      "Your account has been temporarily locked due to too many failed login attempts.",
    );
  } else if (error.message.includes("email not verified")) {
    showError("Please verify your email address before logging in.");
  } else if (error.message.includes("network")) {
    showError(
      "Connection error. Please check your internet connection and try again.",
    );
  } else {
    showError("Login failed. Please try again later.");
  }
}

// Login with remember me functionality
async function loginWithRememberMe(
  credentials: AuthLoginRequest,
  rememberMe: boolean,
) {
  const response = await authApi.login(credentials);

  if (rememberMe) {
    // Store tokens in localStorage for persistence
    storeAuthenticationData(response);
  } else {
    // Store tokens in sessionStorage for session-only persistence
    sessionStorage.setItem("access_token", response.access_token);
    sessionStorage.setItem("refresh_token", response.refresh_token);
    sessionStorage.setItem("token_type", response.token_type);
  }

  return response;
}
```

### Session Management (`logout`)

Securely terminates user sessions and clears authentication data.

```typescript
async function logout(): Promise<AuthLogoutResponse>;
```

**Returns:**

- `Promise<AuthLogoutResponse>` - Logout confirmation response

**Example Usage:**

```typescript
async function handleUserLogout() {
  try {
    // Perform server-side logout
    const response = await authApi.logout();

    console.log("Logout successful:", response.message);

    // Clear all authentication data
    clearAuthenticationData();

    // Clear application state
    clearUserSession();

    // Redirect to login page
    window.location.href = "/login";

    return response;
  } catch (error) {
    console.error("Logout failed:", error.message);

    // Even if server logout fails, clear local data
    clearAuthenticationData();
    clearUserSession();

    // Still redirect to login
    window.location.href = "/login";
  }
}

function clearAuthenticationData() {
  // Remove tokens and user data
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("token_type");
  localStorage.removeItem("user_data");
  localStorage.removeItem("login_timestamp");

  // Clear session storage as well
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
  sessionStorage.removeItem("token_type");
  sessionStorage.removeItem("returnUrl");
}

function clearUserSession() {
  // Clear any application-specific state
  // This would be customized based on your state management solution
  // Example: Clear Zustand store
  // useAuthStore.getState().clearUser();
  // Example: Clear React Query cache
  // queryClient.clear();
}

// Automatic logout on tab close
window.addEventListener("beforeunload", () => {
  const rememberMe = localStorage.getItem("access_token");
  if (!rememberMe) {
    // Only auto-logout if not using "remember me"
    authApi.logout().catch(console.error);
  }
});
```

### Token Management (`refreshToken`)

Automatically refreshes JWT access tokens to maintain user sessions.

```typescript
async function refreshToken(
  refreshToken: string,
): Promise<AuthTokenRefreshResponse>;
```

**Parameters:**

- `refreshToken: string` - Valid refresh token

**Returns:**

- `Promise<AuthTokenRefreshResponse>` - New access token and metadata

**Example Usage:**

```typescript
async function handleTokenRefresh() {
  try {
    const storedRefreshToken =
      localStorage.getItem("refresh_token") ||
      sessionStorage.getItem("refresh_token");

    if (!storedRefreshToken) {
      throw new Error("No refresh token available");
    }

    const response = await authApi.refreshToken(storedRefreshToken);

    console.log("Token refreshed successfully");

    // Update stored tokens
    const storage = localStorage.getItem("refresh_token")
      ? localStorage
      : sessionStorage;
    storage.setItem("access_token", response.access_token);
    storage.setItem("token_type", response.token_type);

    // Update refresh token if provided
    if (response.refresh_token) {
      storage.setItem("refresh_token", response.refresh_token);
    }

    return response;
  } catch (error) {
    console.error("Token refresh failed:", error.message);

    // If refresh fails, user needs to log in again
    clearAuthenticationData();
    window.location.href = "/login";

    throw error;
  }
}

// Automatic token refresh interceptor
class TokenManager {
  private refreshPromise: Promise<AuthTokenRefreshResponse> | null = null;

  async getValidToken(): Promise<string> {
    const token = this.getStoredToken();

    if (!token) {
      throw new Error("No access token available");
    }

    // Check if token is expired or expiring soon
    if (this.isTokenExpired(token) || this.isTokenExpiringSoon(token)) {
      return await this.refreshTokenIfNeeded();
    }

    return token;
  }

  private async refreshTokenIfNeeded(): Promise<string> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      const response = await this.refreshPromise;
      return response.access_token;
    }

    this.refreshPromise = handleTokenRefresh();

    try {
      const response = await this.refreshPromise;
      return response.access_token;
    } finally {
      this.refreshPromise = null;
    }
  }

  private getStoredToken(): string | null {
    return (
      localStorage.getItem("access_token") ||
      sessionStorage.getItem("access_token")
    );
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true; // Assume expired if we can't parse
    }
  }

  private isTokenExpiringSoon(
    token: string,
    bufferMinutes: number = 5,
  ): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const bufferMs = bufferMinutes * 60 * 1000;
      return payload.exp * 1000 < Date.now() + bufferMs;
    } catch {
      return true;
    }
  }
}

export const tokenManager = new TokenManager();
```

### Password Recovery (`forgotPassword` & `resetPassword`)

Complete password reset workflow with email verification.

```typescript
async function forgotPassword(
  resetRequest: AuthPasswordResetRequest,
): Promise<AuthPasswordResetResponse>;
async function resetPassword(
  resetRequest: AuthPasswordResetConfirmRequest,
): Promise<AuthPasswordResetConfirmResponse>;
```

**Example Usage:**

```typescript
// Step 1: Request password reset
async function requestPasswordReset(email: string) {
  try {
    const response = await authApi.forgotPassword({ email });

    console.log("Password reset email sent:", response.message);

    showSuccess(
      "Password reset instructions have been sent to your email address.",
    );

    return response;
  } catch (error) {
    console.error("Password reset request failed:", error.message);

    if (error.message.includes("not found")) {
      showError("No account found with this email address.");
    } else if (error.message.includes("rate limit")) {
      showError("Too many reset requests. Please wait before trying again.");
    } else {
      showError("Failed to send reset email. Please try again later.");
    }

    throw error;
  }
}

// Step 2: Reset password with token
async function confirmPasswordReset(token: string, newPassword: string) {
  try {
    const resetRequest = {
      token,
      new_password: newPassword,
    };

    const response = await authApi.resetPassword(resetRequest);

    console.log("Password reset successful:", response.message);

    showSuccess(
      "Your password has been reset successfully. Please log in with your new password.",
    );

    // Redirect to login page
    setTimeout(() => {
      window.location.href = "/login";
    }, 2000);

    return response;
  } catch (error) {
    console.error("Password reset failed:", error.message);

    if (error.message.includes("invalid token")) {
      showError(
        "Invalid or expired reset token. Please request a new password reset.",
      );
    } else if (error.message.includes("password")) {
      showError("Password does not meet security requirements.");
    } else {
      showError("Failed to reset password. Please try again.");
    }

    throw error;
  }
}

// Complete password reset flow component
class PasswordResetFlow {
  async handleForgotPassword(email: string) {
    // Validate email format
    if (!this.isValidEmail(email)) {
      throw new Error("Please enter a valid email address");
    }

    return await requestPasswordReset(email);
  }

  async handlePasswordReset(
    token: string,
    password: string,
    confirmPassword: string,
  ) {
    // Validate new password
    const passwordErrors = this.validatePassword(password, confirmPassword);
    if (passwordErrors.length > 0) {
      throw new Error(
        `Password validation failed: ${passwordErrors.join(", ")}`,
      );
    }

    return await confirmPasswordReset(token, password);
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private validatePassword(
    password: string,
    confirmPassword: string,
  ): string[] {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push("Password must be at least 8 characters long");
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      errors.push("Password must contain uppercase, lowercase, and number");
    }

    if (password !== confirmPassword) {
      errors.push("Passwords do not match");
    }

    return errors;
  }
}
```

### User Profile Management (`getCurrentUser`)

Retrieves current user profile information and session details.

```typescript
async function getCurrentUser(): Promise<User>;
```

**Returns:**

- `Promise<User>` - Current user profile data

**Example Usage:**

```typescript
async function loadUserProfile() {
  try {
    const user = await authApi.getCurrentUser();

    console.log("User profile loaded:", {
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
    });

    // Update UI with user information
    updateUserInterface(user);

    // Store user data locally
    localStorage.setItem("user_data", JSON.stringify(user));

    return user;
  } catch (error) {
    console.error("Failed to load user profile:", error.message);

    if (error.message.includes("unauthorized")) {
      // Token might be expired or invalid
      console.log("User not authenticated, redirecting to login");
      clearAuthenticationData();
      window.location.href = "/login";
    } else {
      showError("Failed to load user profile. Please refresh the page.");
    }

    throw error;
  }
}

function updateUserInterface(user: User) {
  // Update navigation with user name
  const userNameElement = document.getElementById("user-name");
  if (userNameElement) {
    userNameElement.textContent = user.name;
  }

  // Update avatar or profile picture
  const avatarElement = document.getElementById("user-avatar");
  if (avatarElement) {
    avatarElement.src = user.avatar_url || generateAvatarUrl(user.name);
  }

  // Show/hide admin features based on role
  const adminElements = document.querySelectorAll(".admin-only");
  adminElements.forEach((element) => {
    if (user.role === "admin") {
      element.style.display = "block";
    } else {
      element.style.display = "none";
    }
  });
}

function generateAvatarUrl(name: string): string {
  // Generate a default avatar URL based on user name
  const initials = name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase();

  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=0D8ABC&color=fff`;
}

// Automatic profile refresh
async function setupProfileRefresh() {
  // Refresh user profile every 30 minutes
  setInterval(
    async () => {
      try {
        await loadUserProfile();
        console.log("User profile refreshed");
      } catch (error) {
        console.error("Profile refresh failed:", error.message);
      }
    },
    30 * 60 * 1000,
  ); // 30 minutes
}
```

## Type Definitions

### Authentication Request Types

```typescript
interface AuthRegisterRequest {
  email: string; // User email address (required)
  name?: string; // User full name (optional, defaults to email prefix)
  password: string; // User password (required)
}

interface AuthLoginRequest {
  email: string; // User email address
  password: string; // User password
}

interface AuthPasswordResetRequest {
  email: string; // Email address for password reset
}

interface AuthPasswordResetConfirmRequest {
  token: string; // Password reset token from email
  new_password: string; // New password to set
}
```

### Authentication Response Types

```typescript
interface AuthRegisterResponse {
  user: User; // User profile data
  access_token: string; // JWT access token
  refresh_token: string; // JWT refresh token
  token_type: string; // Token type (always "bearer")
}

interface AuthLoginResponse {
  user: User; // User profile data
  access_token: string; // JWT access token
  refresh_token: string; // JWT refresh token
  token_type: string; // Token type (always "bearer")
}

interface AuthLogoutResponse {
  message: string; // Logout confirmation message
}

interface AuthTokenRefreshResponse {
  access_token: string; // New JWT access token
  refresh_token?: string; // New refresh token (if rotated)
  token_type: string; // Token type (always "bearer")
}

interface AuthPasswordResetResponse {
  message: string; // Reset request confirmation
}

interface AuthPasswordResetConfirmResponse {
  message: string; // Password reset confirmation
}
```

### User Profile Type

```typescript
interface User {
  id: string; // Unique user identifier
  email: string; // User email address
  name: string; // User full name
  role: string; // User role (user, admin, etc.)
  avatar_url?: string; // Profile picture URL (optional)
  created_at: string; // Account creation timestamp
  updated_at: string; // Last profile update timestamp
  email_verified: boolean; // Email verification status
  is_active: boolean; // Account active status
}
```

## Advanced Usage Examples

### Complete Authentication Service

```typescript
import { authApi } from "@/lib/api";

class AuthenticationService {
  private tokenManager = new TokenManager();
  private eventEmitter = new EventTarget();

  // Complete registration flow
  async register(userData: {
    email: string;
    name: string;
    password: string;
    confirmPassword: string;
  }) {
    // Validate input
    const errors = this.validateRegistrationData(userData);
    if (errors.length > 0) {
      throw new Error(`Validation failed: ${errors.join(", ")}`);
    }

    try {
      const response = await authApi.register({
        email: userData.email,
        name: userData.name,
        password: userData.password,
      });

      // Store authentication data
      this.storeAuthData(response);

      // Emit registration event
      this.emit("userRegistered", response.user);

      return response;
    } catch (error) {
      this.emit("registrationFailed", error);
      throw error;
    }
  }

  // Complete login flow
  async login(credentials: AuthLoginRequest, rememberMe: boolean = false) {
    try {
      const response = await authApi.login(credentials);

      // Store authentication data
      this.storeAuthData(response, rememberMe);

      // Load full user profile
      const user = await this.loadUserProfile();

      // Emit login event
      this.emit("userLoggedIn", user);

      return response;
    } catch (error) {
      this.emit("loginFailed", error);
      throw error;
    }
  }

  // Complete logout flow
  async logout() {
    try {
      await authApi.logout();
    } catch (error) {
      console.error("Server logout failed:", error.message);
    } finally {
      // Always clear local data
      this.clearAuthData();
      this.emit("userLoggedOut");
    }
  }

  // Check authentication status
  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await this.tokenManager.getValidToken();
      return !!token;
    } catch {
      return false;
    }
  }

  // Get current user with caching
  async getCurrentUser(): Promise<User | null> {
    try {
      if (!(await this.isAuthenticated())) {
        return null;
      }

      return await authApi.getCurrentUser();
    } catch (error) {
      console.error("Failed to get current user:", error.message);
      return null;
    }
  }

  // Complete password reset flow
  async requestPasswordReset(email: string) {
    try {
      const response = await authApi.forgotPassword({ email });
      this.emit("passwordResetRequested", { email });
      return response;
    } catch (error) {
      this.emit("passwordResetFailed", error);
      throw error;
    }
  }

  async confirmPasswordReset(token: string, newPassword: string) {
    try {
      const response = await authApi.resetPassword({
        token,
        new_password: newPassword,
      });
      this.emit("passwordResetConfirmed");
      return response;
    } catch (error) {
      this.emit("passwordResetConfirmationFailed", error);
      throw error;
    }
  }

  // Utility methods
  private storeAuthData(
    authResponse: AuthLoginResponse | AuthRegisterResponse,
    persistent: boolean = true,
  ) {
    const storage = persistent ? localStorage : sessionStorage;

    storage.setItem("access_token", authResponse.access_token);
    storage.setItem("refresh_token", authResponse.refresh_token);
    storage.setItem("token_type", authResponse.token_type);

    const userData = {
      id: authResponse.user.id,
      email: authResponse.user.email,
      name: authResponse.user.name,
      role: authResponse.user.role,
    };
    storage.setItem("user_data", JSON.stringify(userData));
  }

  private clearAuthData() {
    // Clear localStorage
    ["access_token", "refresh_token", "token_type", "user_data"].forEach(
      (key) => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
      },
    );
  }

  private async loadUserProfile(): Promise<User> {
    return await authApi.getCurrentUser();
  }

  private validateRegistrationData(data: {
    email: string;
    name: string;
    password: string;
    confirmPassword: string;
  }): string[] {
    const errors: string[] = [];

    // Email validation
    if (!this.isValidEmail(data.email)) {
      errors.push("Invalid email format");
    }

    // Name validation
    if (data.name.length < 2) {
      errors.push("Name must be at least 2 characters");
    }

    // Password validation
    if (data.password.length < 8) {
      errors.push("Password must be at least 8 characters");
    }

    if (data.password !== data.confirmPassword) {
      errors.push("Passwords do not match");
    }

    return errors;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private emit(eventType: string, data?: any) {
    this.eventEmitter.dispatchEvent(
      new CustomEvent(eventType, { detail: data }),
    );
  }

  // Event listeners
  addEventListener(type: string, listener: EventListener) {
    this.eventEmitter.addEventListener(type, listener);
  }

  removeEventListener(type: string, listener: EventListener) {
    this.eventEmitter.removeEventListener(type, listener);
  }
}

export const authService = new AuthenticationService();
```

### React Hook Integration

```typescript
import { useState, useEffect } from "react";
import { authService } from "./auth-service";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUser();

    // Listen for auth events
    const handleLogin = (event: CustomEvent) => {
      setUser(event.detail);
      setError(null);
    };

    const handleLogout = () => {
      setUser(null);
      setError(null);
    };

    const handleError = (event: CustomEvent) => {
      setError(event.detail.message);
    };

    authService.addEventListener("userLoggedIn", handleLogin);
    authService.addEventListener("userLoggedOut", handleLogout);
    authService.addEventListener("loginFailed", handleError);

    return () => {
      authService.removeEventListener("userLoggedIn", handleLogin);
      authService.removeEventListener("userLoggedOut", handleLogout);
      authService.removeEventListener("loginFailed", handleError);
    };
  }, []);

  async function loadUser() {
    setLoading(true);
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error("Failed to load user:", error.message);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  const login = async (credentials: AuthLoginRequest, rememberMe?: boolean) => {
    setLoading(true);
    setError(null);
    try {
      await authService.login(credentials, rememberMe);
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: {
    email: string;
    name: string;
    password: string;
    confirmPassword: string;
  }) => {
    setLoading(true);
    setError(null);
    try {
      await authService.register(userData);
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await authService.logout();
    } catch (error) {
      console.error("Logout failed:", error.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    clearError: () => setError(null),
  };
}
```

## Security Considerations

### Token Security

- **Secure Storage**: Tokens are stored in localStorage or sessionStorage based on user preference
- **Automatic Refresh**: Access tokens are automatically refreshed before expiration
- **Token Validation**: Client-side token expiration checking and validation
- **Secure Transmission**: All authentication requests use HTTPS in production

### Password Security

- **Client-side Validation**: Password strength requirements enforced on frontend
- **Secure Transmission**: Passwords are never stored locally and transmitted securely
- **Reset Flow**: Complete password reset workflow with email verification
- **Rate Limiting**: Backend implements rate limiting for authentication attempts

### Session Management

- **Automatic Logout**: Configurable automatic logout on inactivity
- **Concurrent Sessions**: Support for multiple device sessions with proper token management
- **Session Monitoring**: Active session tracking and management
- **Secure Logout**: Complete session cleanup on logout

## Error Handling Patterns

### Comprehensive Error Management

```typescript
class AuthErrorHandler {
  static handleAuthError(error: Error, context: string): string {
    console.error(`Authentication error in ${context}:`, error.message);

    // Network errors
    if (error.message.includes("network") || error.message.includes("fetch")) {
      return "Connection error. Please check your internet connection and try again.";
    }

    // Authentication specific errors
    switch (context) {
      case "register":
        return this.handleRegistrationError(error);
      case "login":
        return this.handleLoginError(error);
      case "logout":
        return this.handleLogoutError(error);
      case "refresh":
        return this.handleRefreshError(error);
      case "password-reset":
        return this.handlePasswordResetError(error);
      default:
        return `Authentication failed: ${error.message}`;
    }
  }

  private static handleRegistrationError(error: Error): string {
    if (error.message.includes("email already exists")) {
      return "This email is already registered. Please use a different email or try logging in.";
    } else if (error.message.includes("password")) {
      return "Password does not meet security requirements. Please choose a stronger password.";
    } else if (error.message.includes("validation")) {
      return "Please check your input and try again.";
    }
    return "Registration failed. Please try again later.";
  }

  private static handleLoginError(error: Error): string {
    if (error.message.includes("invalid credentials")) {
      return "Invalid email or password. Please check your credentials and try again.";
    } else if (error.message.includes("account locked")) {
      return "Your account has been temporarily locked due to too many failed login attempts.";
    } else if (error.message.includes("email not verified")) {
      return "Please verify your email address before logging in.";
    }
    return "Login failed. Please try again later.";
  }

  private static handleLogoutError(error: Error): string {
    return "Logout completed locally. Server logout may have failed.";
  }

  private static handleRefreshError(error: Error): string {
    return "Session expired. Please log in again.";
  }

  private static handlePasswordResetError(error: Error): string {
    if (error.message.includes("not found")) {
      return "No account found with this email address.";
    } else if (error.message.includes("rate limit")) {
      return "Too many reset requests. Please wait before trying again.";
    } else if (error.message.includes("invalid token")) {
      return "Invalid or expired reset token. Please request a new password reset.";
    }
    return "Password reset failed. Please try again later.";
  }
}
```

## Performance Considerations

### Optimization Strategies

- **Token Caching**: Intelligent caching of valid tokens to minimize API calls
- **Request Deduplication**: Prevent multiple simultaneous token refresh requests
- **Lazy Loading**: Load user profile only when needed
- **Background Refresh**: Proactive token refresh to maintain seamless sessions

### Memory Management

```typescript
// Efficient token management
class TokenCache {
  private static tokenCache: string | null = null;
  private static cacheTimestamp: number = 0;
  private static readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  static getToken(): string | null {
    const now = Date.now();
    if (this.tokenCache && now - this.cacheTimestamp < this.CACHE_DURATION) {
      return this.tokenCache;
    }

    // Cache expired, get fresh token
    this.tokenCache =
      localStorage.getItem("access_token") ||
      sessionStorage.getItem("access_token");
    this.cacheTimestamp = now;

    return this.tokenCache;
  }

  static clearCache() {
    this.tokenCache = null;
    this.cacheTimestamp = 0;
  }
}
```

## Backend Integration

### Corresponding Backend Endpoints

This module integrates with the following backend endpoints:

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/logout` - Session termination
- `POST /api/v1/auth/refresh-token` - Token refresh
- `GET /api/v1/auth/me` - Current user profile
- `POST /api/v1/auth/request-password-reset` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset confirmation

### Data Synchronization

- **Type Consistency**: Frontend types match backend schemas exactly
- **Error Code Mapping**: HTTP status codes are consistently handled
- **Token Format**: JWT tokens follow backend implementation exactly
- **Validation Rules**: Client-side validation mirrors server-side rules

## Dependencies

### External Dependencies

- **@/logger**: Application logging service for authentication tracking
- **./base**: Base HTTP client providing the `request` function
- **./types**: TypeScript type definitions for authentication data

### Internal Dependencies

- **TypeScript**: Type safety for authentication operations
- **JWT Handling**: Client-side JWT token parsing and validation
- **Local Storage**: Browser storage for session persistence

## Related Files

- **[index.ts](index.ts.md)**: Main API module that exports authentication functionality
- **[base.ts](base.ts.md)**: Base HTTP client used for all requests
- **[types.ts](types.ts.md)**: TypeScript type definitions
- **[users/](users/index.ts.md)**: User management functionality
- **Backend**: `backend/src/api/v1/auth.py` - corresponding backend implementation

## Implementation Best Practices

### Authentication Flow

- **Secure Token Handling**: Never expose tokens in console logs or error messages
- **Graceful Degradation**: Handle authentication failures gracefully
- **Session Persistence**: Support both persistent and session-only authentication
- **Automatic Recovery**: Implement automatic token refresh and error recovery

### User Experience

- **Clear Feedback**: Provide immediate feedback for all authentication actions
- **Error Messaging**: Show user-friendly error messages with recovery instructions
- **Loading States**: Display appropriate loading indicators during authentication
- **Accessibility**: Ensure authentication forms work with screen readers and keyboards
