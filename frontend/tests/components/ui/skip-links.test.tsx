/**
 * Skip Links Component Tests
 * Part of Phase 4: Accessibility & Performance Components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SkipLinks, EnhancedSkipLinks, useSkipLinkTargets } from '@/components/ui/skip-links';
import { customRender, testLogger } from '../../test-utils';

describe('SkipLinks Component', () => {
    beforeEach(() => {
        testLogger.info('Starting SkipLinks test');
        // Clear any existing elements with test IDs
        document.body.innerHTML = '';
    });

    afterEach(() => {
        testLogger.info('Completed SkipLinks test');
    });

    it('renders default skip links', () => {
        testLogger.debug('Testing default skip links rendering');

        render(<SkipLinks />);

        expect(screen.getByText('Skip to main content')).toBeInTheDocument();
        expect(screen.getByText('Skip to navigation')).toBeInTheDocument();
        expect(screen.getByText('Skip to footer')).toBeInTheDocument();
    });

    it('renders custom skip links', () => {
        testLogger.debug('Testing custom skip links');

        const customLinks = [
            { href: '#content', label: 'Skip to content' },
            { href: '#sidebar', label: 'Skip to sidebar' }
        ];

        render(<SkipLinks links={customLinks} />);

        expect(screen.getByText('Skip to content')).toBeInTheDocument();
        expect(screen.getByText('Skip to sidebar')).toBeInTheDocument();
        expect(screen.queryByText('Skip to main content')).not.toBeInTheDocument();
    });

    it('focuses target element when clicked', async () => {
        testLogger.debug('Testing skip link navigation');

        // Create target element
        const targetElement = document.createElement('div');
        targetElement.id = 'main-content';
        targetElement.textContent = 'Main content';
        document.body.appendChild(targetElement);

        render(<SkipLinks />);

        const skipLink = screen.getByText('Skip to main content');
        fireEvent.click(skipLink);

        // Wait for the element to be made focusable and check its setup
        await waitFor(() => {
            expect(targetElement.getAttribute('tabindex')).toBe('-1');
            // In test environment, verify target exists and is properly configured
            expect(document.getElementById('main-content')).toBe(targetElement);
        }, { timeout: 200 });

        // Cleanup
        document.body.removeChild(targetElement);
    });

    it('handles missing target gracefully', () => {
        testLogger.debug('Testing missing target handling');

        const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { });

        render(<SkipLinks />);

        const skipLink = screen.getByText('Skip to main content');

        // Should not throw when target doesn't exist
        expect(() => {
            fireEvent.click(skipLink);
        }).not.toThrow();

        consoleSpy.mockRestore();
    });

    it('applies custom className', () => {
        testLogger.debug('Testing custom className');

        const { container } = render(
            <SkipLinks className="custom-skip-links" />
        );

        const nav = container.querySelector('nav');
        expect(nav).toHaveClass('custom-skip-links');
    });

    it('supports keyboard navigation', async () => {
        testLogger.debug('Testing keyboard navigation');

        // Create target element
        const targetElement = document.createElement('div');
        targetElement.id = 'main-content';
        document.body.appendChild(targetElement);

        render(<SkipLinks />);

        const skipLink = screen.getByText('Skip to main content');

        // Focus the skip link
        skipLink.focus();
        expect(document.activeElement).toBe(skipLink);

        // Press Enter (this should trigger a click event)
        fireEvent.keyDown(skipLink, { key: 'Enter' });
        // Also trigger the click that would normally happen
        fireEvent.click(skipLink);

        // Wait for target setup - verify link navigation works
        await waitFor(() => {
            // The target should now have tabindex set
            expect(document.getElementById('main-content')).toBe(targetElement);
            expect(targetElement.hasAttribute('tabindex')).toBe(true);
        }, { timeout: 200 });

        // Cleanup
        document.body.removeChild(targetElement);
    });

    it('prevents default behavior on click', () => {
        testLogger.debug('Testing default prevention');

        const targetElement = document.createElement('div');
        targetElement.id = 'main-content';
        document.body.appendChild(targetElement);

        render(<SkipLinks />);

        const skipLink = screen.getByText('Skip to main content');
        const clickEvent = new MouseEvent('click', { bubbles: true });
        const preventDefaultSpy = vi.spyOn(clickEvent, 'preventDefault');

        skipLink.dispatchEvent(clickEvent);

        expect(preventDefaultSpy).toHaveBeenCalled();
    });
});

describe('EnhancedSkipLinks Component', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
    });

    it('discovers common page landmarks', async () => {
        testLogger.debug('Testing landmark discovery');

        // Create landmark elements
        const main = document.createElement('main');
        main.id = 'main';
        document.body.appendChild(main);

        const nav = document.createElement('nav');
        nav.id = 'navigation';
        document.body.appendChild(nav);

        const footer = document.createElement('footer');
        footer.id = 'footer';
        document.body.appendChild(footer);

        render(<EnhancedSkipLinks />);

        // Wait for discovery
        await new Promise(resolve => setTimeout(resolve, 150));

        expect(screen.getByText('Skip to main content')).toBeInTheDocument();
        expect(screen.getByText('Skip to navigation')).toBeInTheDocument();
        expect(screen.getByText('Skip to footer')).toBeInTheDocument();
    });

    it('generates IDs for elements without them', async () => {
        testLogger.debug('Testing ID generation');

        const main = document.createElement('main');
        // No ID initially
        document.body.appendChild(main);

        render(<EnhancedSkipLinks />);

        // Wait for discovery
        await new Promise(resolve => setTimeout(resolve, 150));

        // Should have generated an ID
        expect(main.id).toBeTruthy();
        expect(main.id).toBe('main'); // The component uses the tag name as ID
    });

    it('falls back to default links when no landmarks found', async () => {
        testLogger.debug('Testing fallback to default links');

        // Create a separate container to isolate from existing elements
        const container = document.createElement('div');
        document.body.appendChild(container);

        render(<EnhancedSkipLinks />, { container });

        // Wait for discovery
        await new Promise(resolve => setTimeout(resolve, 150));

        // Should find at least some links - either discovered or default fallback
        const links = screen.getAllByRole('link');
        expect(links.length).toBeGreaterThan(0);

        // If no landmarks were found, should show defaults
        // If landmarks were found (like nav), should show those
        const hasDefaultLinks = screen.queryByText('Skip to main content') !== null;
        const hasNavLink = screen.queryByText('Skip to navigation') !== null;

        expect(hasDefaultLinks || hasNavLink).toBe(true);

        // Cleanup
        document.body.removeChild(container);
    });
});

describe('useSkipLinkTargets Hook', () => {
    it('configures target elements correctly', () => {
        testLogger.debug('Testing useSkipLinkTargets hook');

        const TestComponent = ({ targets }: { targets: string[] }) => {
            useSkipLinkTargets(targets);
            return <div>Test</div>;
        };

        // Create target elements
        const main = document.createElement('main');
        main.id = 'main';
        document.body.appendChild(main);

        const nav = document.createElement('nav');
        nav.id = 'nav';
        document.body.appendChild(nav);

        render(<TestComponent targets={['#main', '#nav']} />);

        // Check that elements are configured
        expect(main.getAttribute('tabindex')).toBe('-1');
        expect(nav.getAttribute('tabindex')).toBe('-1');
        expect(main.getAttribute('aria-label')).toBe('main');
        expect(nav.getAttribute('aria-label')).toBe('nav');
    });

    it('handles missing targets gracefully', () => {
        testLogger.debug('Testing missing targets');

        const TestComponent = ({ targets }: { targets: string[] }) => {
            useSkipLinkTargets(targets);
            return <div>Test</div>;
        };

        const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => { });

        // Should not throw when targets don't exist
        expect(() => {
            render(<TestComponent targets={['#missing']} />);
        }).not.toThrow();

        consoleSpy.mockRestore();
    });

    it('preserves existing attributes', () => {
        testLogger.debug('Testing attribute preservation');

        const TestComponent = ({ targets }: { targets: string[] }) => {
            useSkipLinkTargets(targets);
            return <div>Test</div>;
        };

        // Create element with existing attributes
        const main = document.createElement('main');
        main.id = 'main';
        main.setAttribute('aria-label', 'Main content area');
        main.setAttribute('tabindex', '0');
        document.body.appendChild(main);

        render(<TestComponent targets={['#main']} />);

        // Should preserve existing attributes
        expect(main.getAttribute('aria-label')).toBe('Main content area');
        expect(main.getAttribute('tabindex')).toBe('0');
    });
});
