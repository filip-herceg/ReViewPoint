import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EmptyState } from '@/components/ui/empty-state';

describe('EmptyState Component', () => {
    const defaultProps = {
        title: 'No Data Available',
        testId: 'test-empty-state',
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders basic empty state correctly', () => {
        render(<EmptyState {...defaultProps} />);

        expect(screen.getByTestId('test-empty-state')).toBeInTheDocument();
        expect(screen.getByTestId('test-empty-state-title')).toHaveTextContent('No Data Available');
        expect(screen.getByTestId('test-empty-state-icon')).toBeInTheDocument();
    });

    it('renders description when provided', () => {
        const description = 'There are no items to display at this time.';
        render(<EmptyState {...defaultProps} description={description} />);

        expect(screen.getByTestId('test-empty-state-description')).toHaveTextContent(description);
    });

    it('renders custom icon when provided', () => {
        const customIcon = <div data-testid="custom-icon">Custom Icon</div>;
        render(<EmptyState {...defaultProps} icon={customIcon} />);

        expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
    });

    it('renders primary action button', async () => {
        const mockAction = vi.fn();
        const user = userEvent.setup();

        const action = {
            label: 'Add Item',
            onClick: mockAction,
        };

        render(<EmptyState {...defaultProps} action={action} />);

        const actionButton = screen.getByTestId('test-empty-state-primary-action');
        expect(actionButton).toHaveTextContent('Add Item');

        await user.click(actionButton);
        expect(mockAction).toHaveBeenCalled();
    });

    it('renders secondary action button', async () => {
        const mockSecondaryAction = vi.fn();
        const user = userEvent.setup();

        const secondaryAction = {
            label: 'Learn More',
            onClick: mockSecondaryAction,
            variant: 'outline' as const,
        };

        render(<EmptyState {...defaultProps} secondaryAction={secondaryAction} />);

        const secondaryButton = screen.getByTestId('test-empty-state-secondary-action');
        expect(secondaryButton).toHaveTextContent('Learn More');

        await user.click(secondaryButton);
        expect(mockSecondaryAction).toHaveBeenCalled();
    });

    it('renders both primary and secondary actions', () => {
        const action = {
            label: 'Primary Action',
            onClick: vi.fn(),
        };

        const secondaryAction = {
            label: 'Secondary Action',
            onClick: vi.fn(),
        };

        render(
            <EmptyState
                {...defaultProps}
                action={action}
                secondaryAction={secondaryAction}
            />
        );

        expect(screen.getByTestId('test-empty-state-actions')).toBeInTheDocument();
        expect(screen.getByTestId('test-empty-state-primary-action')).toBeInTheDocument();
        expect(screen.getByTestId('test-empty-state-secondary-action')).toBeInTheDocument();
    });

    it('applies different size variants correctly', () => {
        const { rerender } = render(<EmptyState {...defaultProps} size="sm" />);
        let container = screen.getByTestId('test-empty-state');
        expect(container).toHaveClass('py-8');

        rerender(<EmptyState {...defaultProps} size="md" />);
        container = screen.getByTestId('test-empty-state');
        expect(container).toHaveClass('py-12');

        rerender(<EmptyState {...defaultProps} size="lg" />);
        container = screen.getByTestId('test-empty-state');
        expect(container).toHaveClass('py-16');
    });

    it('applies custom className', () => {
        render(<EmptyState {...defaultProps} className="custom-empty-state" />);

        const container = screen.getByTestId('test-empty-state');
        expect(container).toHaveClass('custom-empty-state');
    });

    it('does not render actions section when no actions provided', () => {
        render(<EmptyState {...defaultProps} />);

        expect(screen.queryByTestId('test-empty-state-actions')).not.toBeInTheDocument();
    });

    it('renders with different button variants', () => {
        const action = {
            label: 'Destructive Action',
            onClick: vi.fn(),
            variant: 'destructive' as const,
        };

        render(<EmptyState {...defaultProps} action={action} />);

        const button = screen.getByTestId('test-empty-state-primary-action');
        expect(button).toHaveClass('bg-destructive');
    });
});
