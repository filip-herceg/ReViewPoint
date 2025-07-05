// Centralized test utilities for frontend tests
// Add more helpers as needed for your project

import { render } from '@testing-library/react';
import type { ReactElement } from 'react';

// Example: Custom render with providers (expand as needed)
export function customRender(ui: ReactElement, options = {}) {
    // You can wrap with context providers here if needed
    return render(ui, { ...options });
}

// No additional templates are included yet, as there are no other common data structures in use.
