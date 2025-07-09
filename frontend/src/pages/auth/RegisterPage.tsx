import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { registerSchema, type RegisterFormData } from '@/lib/validation/authSchemas';
import logger from '@/logger';

const RegisterPage: React.FC = () => {
    const navigate = useNavigate();
    const { register: authRegister, isLoading, error, clearError } = useAuth();

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setError: setFormError,
        clearErrors,
        watch,
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
        mode: 'onBlur',
        defaultValues: {
            name: '',
            email: '',
            password: '',
            confirmPassword: '',
        }
    });

    const watchedValues = watch();

    const onSubmit = async (data: RegisterFormData) => {
        logger.info('Registration form submitted', { email: data.email, name: data.name });

        try {
            clearError();
            clearErrors();

            // Extract the registration data for the API (without confirmPassword)
            const registrationData = {
                email: data.email,
                password: data.password,
                name: data.name,
            };

            await authRegister(registrationData);

            logger.info('Registration successful, navigating to dashboard');
            navigate('/dashboard', { replace: true });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Registration failed. Please try again.';
            logger.error('Registration failed', { error: errorMessage, email: data.email });

            // Set form-level error for specific validation issues
            if (errorMessage.toLowerCase().includes('email')) {
                setFormError('email', { message: errorMessage });
            } else if (errorMessage.toLowerCase().includes('password')) {
                setFormError('password', { message: errorMessage });
            } else if (errorMessage.toLowerCase().includes('name')) {
                setFormError('name', { message: errorMessage });
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
                    <CardTitle className="text-2xl font-bold">Create account</CardTitle>
                    <CardDescription>
                        Join ReViewPoint to start reviewing documents
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
                            <label htmlFor="name" className="text-sm font-medium text-gray-700">
                                Full name
                            </label>
                            <div className="relative">
                                <Input
                                    id="name"
                                    type="text"
                                    autoComplete="name"
                                    placeholder="Enter your full name"
                                    disabled={isLoading || isSubmitting}
                                    className="pl-10"
                                    {...register('name', {
                                        onChange: handleInputChange
                                    })}
                                />
                                <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            </div>
                            {errors.name && (
                                <p className="text-sm text-red-600">{errors.name.message}</p>
                            )}
                        </div>

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
                                    autoComplete="new-password"
                                    placeholder="Create a strong password"
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

                        <div className="space-y-2">
                            <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                                Confirm password
                            </label>
                            <div className="relative">
                                <Input
                                    id="confirmPassword"
                                    type={showConfirmPassword ? 'text' : 'password'}
                                    autoComplete="new-password"
                                    placeholder="Confirm your password"
                                    disabled={isLoading || isSubmitting}
                                    className="pl-10 pr-10"
                                    {...register('confirmPassword', {
                                        onChange: handleInputChange
                                    })}
                                />
                                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                <button
                                    type="button"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                                    disabled={isLoading || isSubmitting}
                                >
                                    {showConfirmPassword ? (
                                        <EyeOff className="h-4 w-4" />
                                    ) : (
                                        <Eye className="h-4 w-4" />
                                    )}
                                </button>
                            </div>
                            {errors.confirmPassword && (
                                <p className="text-sm text-red-600">{errors.confirmPassword.message}</p>
                            )}
                        </div>

                        <div className="flex items-start">
                            <div className="flex items-center h-5">
                                <input
                                    id="terms"
                                    name="terms"
                                    type="checkbox"
                                    required
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                            </div>
                            <div className="ml-3 text-sm">
                                <label htmlFor="terms" className="text-gray-700">
                                    I agree to the{' '}
                                    <Link to="/terms" className="text-blue-600 hover:text-blue-500">
                                        Terms of Service
                                    </Link>{' '}
                                    and{' '}
                                    <Link to="/privacy" className="text-blue-600 hover:text-blue-500">
                                        Privacy Policy
                                    </Link>
                                </label>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            disabled={isLoading || isSubmitting || !watchedValues.name || !watchedValues.email || !watchedValues.password || !watchedValues.confirmPassword}
                            className="w-full"
                        >
                            {(isLoading || isSubmitting) ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                    Creating account...
                                </>
                            ) : (
                                'Create account'
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-gray-600">
                            Already have an account?{' '}
                            <Link
                                to="/auth/login"
                                className="font-medium text-blue-600 hover:text-blue-500"
                            >
                                Sign in here
                            </Link>
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default RegisterPage;
