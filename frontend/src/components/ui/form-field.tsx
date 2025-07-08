import React from 'react';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import logger from '@/logger';

export interface FormFieldProps {
    name: string;
    label: string;
    type?: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select';
    placeholder?: string;
    value?: string | number;
    error?: string;
    required?: boolean;
    disabled?: boolean;
    options?: Array<{ value: string; label: string }>;
    onChange?: (value: string) => void;
    onBlur?: () => void;
    className?: string;
    testId?: string;
}

/**
 * FormField component provides a consistent form field with label, input, and error handling
 * Supports various input types and validation states
 */
export function FormField({
    name,
    label,
    type = 'text',
    placeholder,
    value = '',
    error,
    required = false,
    disabled = false,
    options = [],
    onChange,
    onBlur,
    className,
    testId,
}: FormFieldProps) {
    const fieldId = `field-${name}`;
    const errorId = `${fieldId}-error`;

    const handleChange = (newValue: string) => {
        try {
            logger.debug('Form field value changed', { name, type, value: newValue });
            onChange?.(newValue);
        } catch (err) {
            logger.error('Error in form field onChange', err);
        }
    };

    const handleBlur = () => {
        try {
            logger.debug('Form field blurred', { name, type });
            onBlur?.();
        } catch (err) {
            logger.error('Error in form field onBlur', err);
        }
    };

    const renderInput = () => {
        const inputProps = {
            id: fieldId,
            name,
            placeholder,
            value: String(value),
            disabled,
            onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
                handleChange(e.target.value),
            onBlur: handleBlur,
            'aria-describedby': error ? errorId : undefined,
            'aria-invalid': !!error,
            'data-testid': testId ? `${testId}-input` : `${fieldId}-input`,
            className: cn(
                error && 'border-destructive focus-visible:ring-destructive'
            ),
        };

        switch (type) {
            case 'textarea':
                return (
                    <Textarea
                        {...inputProps}
                        rows={4}
                    />
                );

            case 'select':
                return (
                    <Select
                        value={String(value)}
                        onValueChange={handleChange}
                        disabled={disabled}
                    >
                        <SelectTrigger
                            id={fieldId}
                            aria-describedby={error ? errorId : undefined}
                            aria-invalid={!!error}
                            data-testid={testId ? `${testId}-select` : `${fieldId}-select`}
                            className={cn(
                                error && 'border-destructive focus-visible:ring-destructive'
                            )}
                        >
                            <SelectValue placeholder={placeholder} />
                        </SelectTrigger>
                        <SelectContent>
                            {options.map((option) => (
                                <SelectItem
                                    key={option.value}
                                    value={option.value}
                                    data-testid={testId ? `${testId}-option-${option.value}` : `${fieldId}-option-${option.value}`}
                                >
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                );

            default:
                return (
                    <Input
                        {...inputProps}
                        type={type}
                    />
                );
        }
    };

    return (
        <div className={cn('space-y-2', className)} data-testid={testId || fieldId}>
            <Label
                htmlFor={fieldId}
                className={cn(
                    'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
                    required && "after:content-['*'] after:ml-0.5 after:text-destructive"
                )}
                data-testid={testId ? `${testId}-label` : `${fieldId}-label`}
            >
                {label}
            </Label>

            {renderInput()}

            {error && (
                <p
                    id={errorId}
                    className="text-sm font-medium text-destructive"
                    data-testid={testId ? `${testId}-error` : `${fieldId}-error`}
                >
                    {error}
                </p>
            )}
        </div>
    );
}

export default FormField;
