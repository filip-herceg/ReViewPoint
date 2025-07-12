import { CheckCircle, Eye, EyeOff, Lock } from "lucide-react";
import type React from "react";
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const ResetPasswordPage: React.FC = () => {
	const _navigate = useNavigate();
	const [searchParams] = useSearchParams();
	const token = searchParams.get("token");

	const [formData, setFormData] = useState({
		password: "",
		confirmPassword: "",
	});
	const [showPassword, setShowPassword] = useState(false);
	const [showConfirmPassword, setShowConfirmPassword] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState("");
	const [isSuccess, setIsSuccess] = useState(false);

	// If no token is present, show error
	if (!token) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
				<Card className="w-full max-w-md">
					<CardHeader className="text-center">
						<CardTitle className="text-2xl font-bold text-destructive">
							Invalid Reset Link
						</CardTitle>
						<CardDescription>
							This password reset link is invalid or has expired
						</CardDescription>
					</CardHeader>
					<CardContent className="text-center">
						<p className="text-sm text-muted-foreground mb-4">
							Please request a new password reset link to continue.
						</p>
						<div className="space-y-2">
							<Button asChild className="w-full">
								<Link to="/auth/forgot-password">
									<span>Request new reset link</span>
								</Link>
							</Button>
							<Button variant="outline" asChild className="w-full">
								<Link to="/auth/login">
									<span>Back to sign in</span>
								</Link>
							</Button>
						</div>
					</CardContent>
				</Card>
			</div>
		);
	}

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError("");

		// Validation
		if (formData.password !== formData.confirmPassword) {
			setError("Passwords do not match");
			return;
		}

		if (formData.password.length < 8) {
			setError("Password must be at least 8 characters long");
			return;
		}

		setIsLoading(true);

		try {
			// TODO: Replace with actual API call
			await new Promise((resolve) => setTimeout(resolve, 1000));

			setIsSuccess(true);
		} catch (_err) {
			setError("Failed to reset password. Please try again.");
		} finally {
			setIsLoading(false);
		}
	};

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setFormData((prev) => ({
			...prev,
			[e.target.name]: e.target.value,
		}));
		// Clear error when user starts typing
		if (error) setError("");
	};

	if (isSuccess) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
				<Card className="w-full max-w-md">
					<CardHeader className="text-center">
						<div className="mx-auto w-12 h-12 bg-success/10 rounded-full flex items-center justify-center mb-4">
							<CheckCircle className="w-6 h-6 text-success-foreground" />
						</div>
						<CardTitle className="text-2xl font-bold text-success-foreground">
							Password Reset Successful
						</CardTitle>
						<CardDescription>
							Your password has been successfully reset
						</CardDescription>
					</CardHeader>
					<CardContent className="text-center">
						<p className="text-sm text-muted-foreground mb-6">
							You can now sign in with your new password.
						</p>
						<Button asChild className="w-full">
							<Link to="/auth/login">
								<span>Sign in to your account</span>
							</Link>
						</Button>
					</CardContent>
				</Card>
			</div>
		);
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
			<Card className="w-full max-w-md">
				<CardHeader className="text-center">
					<CardTitle className="text-2xl font-bold text-foreground">
						Reset your password
					</CardTitle>
					<CardDescription>Enter your new password below</CardDescription>
				</CardHeader>
				<CardContent>
					<form onSubmit={handleSubmit} className="space-y-4">
						{error && (
							<div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-md text-sm">
								{error}
							</div>
						)}

						<div className="space-y-2">
							<label
								htmlFor="password"
								className="text-sm font-medium text-foreground"
							>
								New password
							</label>
							<div className="relative">
								<Input
									id="password"
									name="password"
									type={showPassword ? "text" : "password"}
									autoComplete="new-password"
									required
									placeholder="Enter your new password"
									value={formData.password}
									onChange={handleChange}
									disabled={isLoading}
									className="pl-10 pr-10"
								/>
								<Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
								<Button
									type="button"
									variant="ghost"
									size="icon-sm"
									onClick={() => setShowPassword(!showPassword)}
									className="absolute right-3 top-3"
									disabled={isLoading}
								>
									{showPassword ? (
										<EyeOff className="h-4 w-4" />
									) : (
										<Eye className="h-4 w-4" />
									)}
								</Button>
							</div>
							<p className="text-xs text-muted-foreground">
								Password must be at least 8 characters long
							</p>
						</div>

						<div className="space-y-2">
							<label
								htmlFor="confirmPassword"
								className="text-sm font-medium text-foreground"
							>
								Confirm new password
							</label>
							<div className="relative">
								<Input
									id="confirmPassword"
									name="confirmPassword"
									type={showConfirmPassword ? "text" : "password"}
									autoComplete="new-password"
									required
									placeholder="Confirm your new password"
									value={formData.confirmPassword}
									onChange={handleChange}
									disabled={isLoading}
									className="pl-10 pr-10"
								/>
								<Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
								<Button
									type="button"
									variant="ghost"
									size="icon-sm"
									onClick={() => setShowConfirmPassword(!showConfirmPassword)}
									className="absolute right-3 top-3"
									disabled={isLoading}
								>
									{showConfirmPassword ? (
										<EyeOff className="h-4 w-4" />
									) : (
										<Eye className="h-4 w-4" />
									)}
								</Button>
							</div>
						</div>

						<Button
							type="submit"
							disabled={
								isLoading || !formData.password || !formData.confirmPassword
							}
							className="w-full"
						>
							{isLoading ? (
								<>
									<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary mr-2"></div>
									Resetting password...
								</>
							) : (
								"Reset password"
							)}
						</Button>
					</form>

					<div className="mt-6 text-center">
						<Link
							to="/auth/login"
							className="text-sm text-primary hover:text-primary/80"
						>
							Back to sign in
						</Link>
					</div>
				</CardContent>
			</Card>
		</div>
	);
};

export default ResetPasswordPage;
