/**
 * Authentication Form Validation Schemas
 *
 * Zod schemas for validating authentication forms on the frontend.
 * These schemas ensure data consistency and provide user-friendly error messages.
 *
 * Features:
 * - Email validation with proper formatting
 * - Password strength requirements
 * - Password confirmation validation
 * - Name validation for registration
 * - Token validation for reset flows
 * - Consistent error messaging
 *
 * @example
 * ```typescript
 * import { loginSchema, registerSchema } from '@/lib/validation/authSchemas';
 *
 * const result = loginSchema.safeParse({
 *   email: 'user@example.com',
 *   password: 'password123'
 * });
 *
 * if (result.success) {
 *   // Form data is valid
 *   console.log(result.data);
 * } else {
 *   // Show validation errors
 *   console.log(result.error.issues);
 * }
 * ```
 */

import { z } from "zod";
import logger from "@/logger";
import { EMAIL_REGEX, DEFAULT_PASSWORD_REQUIREMENTS } from "@/lib/api/types";

// ===========================
// Base validation utilities
// ===========================

/**
 * Email validation schema
 * Uses the same regex pattern as the backend for consistency
 */
export const emailSchema = z
  .string()
  .min(1, "Email is required")
  .email("Please enter a valid email address")
  .regex(EMAIL_REGEX, "Please enter a valid email address")
  .max(254, "Email address is too long") // RFC 5321 limit
  .transform((email) => email.toLowerCase().trim());

/**
 * Password validation schema
 * Matches backend requirements for consistency:
 * - At least 8 characters
 * - At least one letter (any case)
 * - At least one digit
 */
export const passwordSchema = z
  .string()
  .min(
    DEFAULT_PASSWORD_REQUIREMENTS.minLength,
    `Password must be at least ${DEFAULT_PASSWORD_REQUIREMENTS.minLength} characters`,
  )
  .max(
    DEFAULT_PASSWORD_REQUIREMENTS.maxLength,
    `Password must be no more than ${DEFAULT_PASSWORD_REQUIREMENTS.maxLength} characters`,
  )
  .refine(
    (password) => /[A-Za-z]/.test(password),
    "Password must contain at least one letter",
  )
  .refine((password) => {
    if (!DEFAULT_PASSWORD_REQUIREMENTS.requiresNumber) return true;
    return /\d/.test(password);
  }, "Password must contain at least one digit")
  .refine((password) => {
    if (!DEFAULT_PASSWORD_REQUIREMENTS.requiresUppercase) return true;
    return /[A-Z]/.test(password);
  }, "Password must contain at least one uppercase letter")
  .refine((password) => {
    if (!DEFAULT_PASSWORD_REQUIREMENTS.requiresLowercase) return true;
    return /[a-z]/.test(password);
  }, "Password must contain at least one lowercase letter")
  .refine((password) => {
    if (!DEFAULT_PASSWORD_REQUIREMENTS.requiresSpecial) return true;
    return /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  }, "Password must contain at least one special character");

/**
 * Name validation schema
 */
export const nameSchema = z
  .string()
  .min(1, "Name is required")
  .min(2, "Name must be at least 2 characters")
  .max(100, "Name must be no more than 100 characters")
  .regex(
    /^[a-zA-Z\s'-]+$/,
    "Name can only contain letters, spaces, hyphens, and apostrophes",
  )
  .transform((name) => name.trim());

/**
 * Token validation schema (for password reset, email verification, etc.)
 */
export const tokenSchema = z
  .string()
  .min(1, "Token is required")
  .min(10, "Invalid token format")
  .max(500, "Token is too long");

// ===========================
// Authentication form schemas
// ===========================

/**
 * Login form validation schema
 */
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, "Password is required"),
});

// Separate type for login form that includes remember me
export type LoginFormData = z.infer<typeof loginSchema> & {
  rememberMe?: boolean;
};

/**
 * Registration form validation schema
 */
export const registerSchema = z
  .object({
    name: nameSchema,
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;

/**
 * Forgot password form validation schema
 */
export const forgotPasswordSchema = z.object({
  email: emailSchema,
});

export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

/**
 * Reset password form validation schema
 */
export const resetPasswordSchema = z
  .object({
    token: tokenSchema,
    password: passwordSchema,
    confirmPassword: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

/**
 * Change password form validation schema (for authenticated users)
 */
export const changePasswordSchema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: passwordSchema,
    confirmNewPassword: z.string().min(1, "Please confirm your new password"),
  })
  .refine((data) => data.newPassword === data.confirmNewPassword, {
    message: "New passwords do not match",
    path: ["confirmNewPassword"],
  })
  .refine((data) => data.currentPassword !== data.newPassword, {
    message: "New password must be different from current password",
    path: ["newPassword"],
  });

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

// ===========================
// Utility functions
// ===========================

/**
 * Get user-friendly validation error messages
 */
export function getValidationErrors(error: z.ZodError): Record<string, string> {
  const errors: Record<string, string> = {};

  for (const issue of error.issues) {
    const path = issue.path.join(".");
    if (path) {
      errors[path] = issue.message;
    }
  }

  logger.debug("Validation errors extracted", {
    errorCount: error.issues.length,
    fields: Object.keys(errors),
  });

  return errors;
}

/**
 * Validate form data and return formatted errors
 */
export function validateFormData<T>(
  schema: z.ZodSchema<T>,
  data: unknown,
):
  | { success: true; data: T }
  | { success: false; errors: Record<string, string> } {
  try {
    const result = schema.safeParse(data);

    if (result.success) {
      logger.debug("Form validation successful");
      return { success: true, data: result.data };
    } else {
      const errors = getValidationErrors(result.error);
      logger.warn("Form validation failed", { errors });
      return { success: false, errors };
    }
  } catch (error) {
    logger.error("Unexpected validation error", { error });
    return {
      success: false,
      errors: { _form: "An unexpected validation error occurred" },
    };
  }
}

/**
 * Create a custom validation function for React Hook Form
 */
export function createValidator<T>(schema: z.ZodSchema<T>) {
  return (data: unknown) => {
    const result = validateFormData(schema, data);
    if (result.success) {
      return true;
    } else {
      // Return the first error for React Hook Form
      const firstError = Object.values(result.errors)[0];
      return firstError || "Validation failed";
    }
  };
}

// ===========================
// Re-export for convenience
// ===========================

export { EMAIL_REGEX, DEFAULT_PASSWORD_REQUIREMENTS } from "@/lib/api/types";
