import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Lock, Mail, XCircle } from "lucide-react";
import type React from "react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { type LoginFormData, loginSchema } from "@/lib/validation/authSchemas";
import logger from "@/logger";

const LoginPage: React.FC = () => {
	const navigate = useNavigate();
	const location = useLocation();
	const { login, isLoading, error, clearError } = useAuth();

	const [showPassword, setShowPassword] = useState(false);

	// Get the intended destination from location state
	const from = (location.state as any)?.from?.pathname || "/dashboard";

	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting },
		setError: setFormError,
		clearErrors,
		watch,
	} = useForm<LoginFormData>({
		resolver: zodResolver(loginSchema),
		mode: "onBlur",
		defaultValues: {
			email: "",
			password: "",
			rememberMe: false,
		},
	});

	const watchedValues = watch();

	const onSubmit = async (data: LoginFormData) => {
		logger.info("Login form submitted", { email: data.email });

		try {
			clearError();
			clearErrors();

			// Extract the login credentials for the API
			const loginCredentials = {
				email: data.email,
				password: data.password,
			};

			await login(loginCredentials, data.rememberMe || false);

			logger.info("Login successful, navigating to dashboard");
			navigate(from, { replace: true });
		} catch (err) {
			const errorMessage =
				err instanceof Error ? err.message : "Login failed. Please try again.";
			logger.error("Login failed", { error: errorMessage, email: data.email });

			// Set form-level error for specific validation issues
			if (errorMessage.toLowerCase().includes("email")) {
				setFormError("email", { message: errorMessage });
			} else if (errorMessage.toLowerCase().includes("password")) {
				setFormError("password", { message: errorMessage });
			}
			// General errors are handled by useAuth error state
		}
	};

	const handleInputChange = () => {
		// Clear general error when user starts typing
		if (error) {
			clearError();
		}
		clearErrors();
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-muted/30 to-accent/10 py-12 px-4 sm:px-6 lg:px-8">
			<div className="w-full max-w-md">
				{/* Decorative background */}
				<div className="absolute inset-0 -z-10 opacity-20">
					<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-conic from-primary/20 via-accent/10 to-primary/20 rounded-full blur-3xl"></div>
				</div>

				<Card className="glass-card hover-lift animate-fade-in">
					<CardHeader className="text-center space-y-4">
						<CardTitle className="text-3xl font-bold bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
							Welcome back
						</CardTitle>
						<CardDescription className="text-body-lg">
							Sign in to your ReViewPoint account
						</CardDescription>
					</CardHeader>
					<CardContent>
						<form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
							{error && (
								<div className="p-4 rounded-lg bg-destructive/10 border border-destructive animate-slide-up">
									<p className="text-sm text-destructive flex items-center gap-2">
										<XCircle className="h-4 w-4" />
										{error}
									</p>
								</div>
							)}

							<div className="space-y-2">
								<label
									htmlFor="email"
									className="text-sm font-medium text-foreground"
								>
									Email address
								</label>
								<div className="relative">
									<Input
										id="email"
										type="email"
										autoComplete="email"
										placeholder="Enter your email"
										disabled={isLoading || isSubmitting}
										className="pl-10"
										{...register("email", {
											onChange: handleInputChange,
										})}
									/>
									<Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
								</div>
								{errors.email && (
									<p className="text-sm text-destructive">
										{errors.email.message}
									</p>
								)}
							</div>

							<div className="space-y-2">
								<label
									htmlFor="password"
									className="text-sm font-medium text-foreground"
								>
									Password
								</label>
								<div className="relative">
									<Input
										id="password"
										type={showPassword ? "text" : "password"}
										autoComplete="current-password"
										placeholder="Enter your password"
										disabled={isLoading || isSubmitting}
										className="pl-10 pr-10"
										{...register("password", {
											onChange: handleInputChange,
										})}
									/>
									<Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
									<Button
										type="button"
										variant="ghost"
										size="icon-sm"
										onClick={() => setShowPassword(!showPassword)}
										className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
										disabled={isLoading || isSubmitting}
									>
										{showPassword ? (
											<EyeOff className="h-4 w-4" />
										) : (
											<Eye className="h-4 w-4" />
										)}
									</Button>
								</div>
								{errors.password && (
									<p className="text-sm text-destructive">
										{errors.password.message}
									</p>
								)}
							</div>

							<div className="flex items-center justify-between">
								<div className="flex items-center">
									<input
										id="remember-me"
										type="checkbox"
										className="h-4 w-4 text-primary focus:ring-primary border-border rounded"
										{...register("rememberMe")}
									/>
									<label
										htmlFor="remember-me"
										className="ml-2 block text-sm text-foreground"
									>
										Remember me
									</label>
								</div>

								<Link
									to="/auth/forgot-password"
									className="text-sm text-primary hover:text-primary/80"
								>
									Forgot your password?
								</Link>
							</div>

							<Button
								type="submit"
								disabled={
									isLoading ||
									isSubmitting ||
									!watchedValues.email ||
									!watchedValues.password
								}
								className="w-full"
							>
								{isLoading || isSubmitting ? (
									<>
										<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
										Signing in...
									</>
								) : (
									"Sign in"
								)}
							</Button>
						</form>

						<div className="mt-6 text-center">
							<p className="text-sm text-muted-foreground">
								Don't have an account?{" "}
								<Link
									to="/auth/register"
									className="font-medium text-primary hover:text-primary/80"
								>
									Sign up here
								</Link>
							</p>
						</div>

						{/* Demo Account Info */}
						<div className="mt-6 p-4 bg-accent border border-border rounded-md">
							<h4 className="text-sm font-medium text-accent-foreground mb-2">
								Demo Account
							</h4>
							<p className="text-xs text-muted-foreground mb-2">
								For testing, you can use any email and password combination.
							</p>
							<div className="text-xs text-primary">
								<p>Email: demo@example.com</p>
								<p>Password: password123</p>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
};

export default LoginPage;
