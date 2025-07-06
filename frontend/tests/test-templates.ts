// Utility: Create a test error object for error handling tests
export function createTestError(message: string | Error = 'Test error'): Error {
    // If the message is already an Error, return it directly instead of wrapping it
    if (message instanceof Error) {
        testLogger.debug('Returning existing error object', message);
        return message;
    }

    const err = new Error(message);
    testLogger.debug('Created test error object', err);
    return err;
}
// Centralized test data templates (factories) for frontend tests
// Use these to generate consistent test data in all tests
// You can import utilities from test-utils as needed

import { randomString, randomInt, randomDate, testLogger } from './test-utils';
import { QueryClient } from '@tanstack/react-query';

// Utility to clear all react-query caches for test isolation
export function clearReactQueryCache() {
    // If you use a global QueryClient, clear it here. Otherwise, clear all caches in your test setup.
    // This is a no-op placeholder for now, but you can call this in beforeEach/afterEach in tests.
    // If you use a custom QueryClient instance, call queryClient.clear() in your test file.
    // Example:
    // queryClient.clear();
    // For global cache: QueryClient.clear();
    // (No-op for now)
    testLogger.info('Cleared react-query cache (noop placeholder)');
}

// Update Upload type to match app (pending | uploading | completed | error)
export type Upload = {
    id: string;
    name: string;
    status: 'pending' | 'uploading' | 'completed' | 'error';
    progress: number;
    createdAt: string;
};

import { randomStatus } from './test-utils';

// Pick a random status for Upload
export function randomUploadStatus(): Upload['status'] {
    const statuses: Upload['status'][] = ['pending', 'uploading', 'completed', 'error'];
    const status = statuses[randomInt(0, statuses.length - 1)];
    if (status === 'error') {
        testLogger.warn('Picked random upload status: error');
    } else {
        testLogger.debug('Picked random upload status:', status);
    }
    return status;
}

export function createUpload(overrides: Partial<Upload> = {}): Upload {
    const upload: Upload = {
        id: overrides.id || randomString(6),
        name: overrides.name || `${randomString(4)}.pdf`,
        status: overrides.status || randomUploadStatus(),
        progress: overrides.progress ?? randomInt(0, 100),
        createdAt: overrides.createdAt || randomDate(),
        ...overrides,
    };
    if (upload.status === 'error') {
        testLogger.error('Created upload with error status', upload);
    } else if (upload.progress === 0) {
        testLogger.info('Created upload with 0% progress', upload);
    } else {
        testLogger.debug('Created upload object', upload);
    }
    return upload;

}


// Create an array of uploads (for UploadList tests)
export function createUploadList(count = 3, overrides: Partial<Upload> = {}): Upload[] {
    const list = Array.from({ length: count }, () => createUpload(overrides));
    if (count > 10) {
        testLogger.warn(`Created large upload list of length ${count}`);
    } else {
        testLogger.info(`Created upload list of length ${count}`, list);
    }
    return list;
}

// If you add user/auth features, add user templates here
// export function createUser(...) { ... }

// User type for authStore
export type User = {
    id: string;
    username: string;
    email: string;
    roles: string[];
};

export function createUser(overrides: Partial<User> = {}): User {
    const user = {
        id: overrides.id || randomString(6),
        username: overrides.username || 'user_' + randomString(4),
        email: overrides.email || randomString(5) + '@example.com',
        roles: overrides.roles || ['user'],
        ...overrides,
    };
    if (user.roles && user.roles.includes('admin')) {
        testLogger.info('Created admin user', user);
    } else {
        testLogger.debug('Created user', user);
    }
    return user;
}

// Template for upload form data (matches UploadForm initial state)
export type UploadFormData = {
    name: string;
    status: 'pending';
    progress: number;
};

export function createUploadFormData(overrides: Partial<UploadFormData> = {}): UploadFormData {
    const formData: UploadFormData = {
        ...overrides,
        name: overrides.name || randomString(8) + '.pdf',
        progress: 0,
        status: 'pending', // Always force status to 'pending' to satisfy UploadFormData type
    };
    if (formData.name.endsWith('.pdf')) {
        testLogger.debug('Created upload form data for PDF', formData);
    } else {
        testLogger.info('Created upload form data', formData);
    }
    return formData;
}

// If you add forms, add form data templates here
// export function createUploadFormData(...) { ... }

// Template for plausible analytics event
export type AnalyticsEvent = {
    name: string;
    props?: Record<string, any>;
};

export function createAnalyticsEvent(overrides: Partial<AnalyticsEvent> = {}): AnalyticsEvent {
    const event = {
        name: overrides.name || 'test_event_' + randomString(5),
        props: overrides.props || { foo: randomString(3) },
        ...overrides,
    };
    if (event.name.startsWith('test_event_')) {
        testLogger.debug('Created test analytics event', event);
    } else {
        testLogger.info('Created analytics event', event);
    }
    return event;
}

// Template for button props (for UI tests)
export type ButtonProps = {
    variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
    size?: 'default' | 'sm' | 'lg' | 'icon';
    className?: string;
    children?: string;
    asChild?: boolean;
    [key: string]: any;
};

export function createButtonProps(overrides: Partial<ButtonProps> = {}): ButtonProps {
    const variants = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'] as const;
    const sizes = ['default', 'sm', 'lg', 'icon'] as const;
    const btn = {
        variant: overrides.variant || variants[randomInt(0, variants.length - 1)],
        size: overrides.size || sizes[randomInt(0, sizes.length - 1)],
        className: overrides.className || '',
        children: overrides.children || 'Button',
        asChild: overrides.asChild ?? false,
        ...overrides,
    };
    if (btn.variant === 'destructive') {
        testLogger.warn('Created destructive button props', btn);
    } else {
        testLogger.debug('Created button props', btn);
    }
    return btn;
}

// Template for input props (for UI tests)
export type InputProps = {
    className?: string;
    type?: string;
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    [key: string]: any;
};

export function createInputProps(overrides: Partial<InputProps> = {}): InputProps {
    const types = ['text', 'email', 'password', 'number', 'file'] as const;
    const input = {
        className: overrides.className || '',
        type: overrides.type || types[randomInt(0, types.length - 1)],
        value: overrides.value || randomString(8),
        placeholder: overrides.placeholder || 'Enter value',
        disabled: overrides.disabled ?? false,
        ...overrides,
    };
    if (input.type === 'password') {
        testLogger.info('Created password input props', input);
    } else {
        testLogger.debug('Created input props', input);
    }
    return input;
}

// Template for card props (for UI tests)
export type CardProps = {
    className?: string;
    children?: React.ReactNode;
    [key: string]: any;
};

export function createCardProps(overrides: Partial<CardProps> = {}): CardProps {
    const card = {
        className: overrides.className || '',
        children: overrides.children || 'Card Content',
        ...overrides,
    };
    if (card.className && card.className.includes('highlight')) {
        testLogger.info('Created highlighted card props', card);
    } else {
        testLogger.debug('Created card props', card);
    }
    return card;
}
