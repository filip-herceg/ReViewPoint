import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { loginSchema, type LoginFormData } from '@/lib/validation/authSchemas';
import logger from '@/logger';

const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { login, isLoading, error, clearError } = useAuth();

    const [showPassword, setShowPassword] = useState(false);

    // Get the intended destination from location state
    const from = (location.state as any)?.from?.pathname || '/dashboard';

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setError: setFormError,
        clearErrors,
        watch,
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        mode: 'onBlur',
        defaultValues: {
            email: '',
            password: '',
            rememberMe: false,
        }
    });

    const watchedValues = watch();

    const onSubmit = async (data: LoginFormData) => {
        logger.info('Login form submitted', { email: data.email });

        try {
            clearError();
            clearErrors();

            // Extract the login credentials for the API
            const loginCredentials = {
                email: data.email,
                password: data.password,
            };

            await login(loginCredentials, data.rememberMe || false);

            logger.info('Login successful, navigating to dashboard');
            navigate(from, { replace: true });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Login failed. Please try again.';
            logger.error('Login failed', { error: errorMessage, email: data.email });

            // Set form-level error for specific validation issues
            if (errorMessage.toLowerCase().includes('email')) {
                setFormError('email', { message: errorMessage });
            } else if (errorMessage.toLowerCase().includes('password')) {
                setFormError('password', { message: errorMessage });
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
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
                    <CardDescription>
                        Sign in to your ReViewPoint account
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label htmlFor="email" className="text-sm font-medium text-gray-700">
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
                                    {...register('email', {
                                        onChange: handleInputChange
                                    })}
                                />
                                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            </div>
                            {errors.email && (
                                <p className="text-sm text-red-600">{errors.email.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-medium text-gray-700">
                                Password
                            </label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    autoComplete="current-password"
                                    placeholder="Enter your password"
                                    disabled={isLoading || isSubmitting}
                                    className="pl-10 pr-10"
                                    {...register('password', {
                                        onChange: handleInputChange
                                    })}
                                />
                                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                                    disabled={isLoading || isSubmitting}
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-4 w-4" />
                                    ) : (
                                        <Eye className="h-4 w-4" />
                                    )}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="text-sm text-red-600">{errors.password.message}</p>
                            )}
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <input
                                    id="remember-me"
                                    type="checkbox"
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    {...register('rememberMe')}
                                />
                                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                                    Remember me
                                </label>
                            </div>

                            <Link
                                to="/auth/forgot-password"
                                className="text-sm text-blue-600 hover:text-blue-500"
                            >
                                Forgot your password?
                            </Link>
                        </div>

                        <Button
                            type="submit"
                            disabled={isLoading || isSubmitting || !watchedValues.email || !watchedValues.password}
                            className="w-full"
                        >
                            {(isLoading || isSubmitting) ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-gray-600">
                            Don't have an account?{' '}
                            <Link
                                to="/auth/register"
                                className="font-medium text-blue-600 hover:text-blue-500"
                            >
                                Sign up here
                            </Link>
                        </p>
                    </div>

                    {/* Demo Account Info */}
                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
                        <h4 className="text-sm font-medium text-blue-900 mb-2">Demo Account</h4>
                        <p className="text-xs text-blue-700 mb-2">
                            For testing, you can use any email and password combination.
                        </p>
                        <div className="text-xs text-blue-600">
                            <p>Email: demo@example.com</p>
                            <p>Password: password123</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default LoginPage;
