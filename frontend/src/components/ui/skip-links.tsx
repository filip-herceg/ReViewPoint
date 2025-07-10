/**
 * Skip Links Component
 * Provides keyboard navigation accessibility for screen readers
 * Part of Phase 4: Accessibility & Performance Components
 */

import React from 'react';
import { cn } from '@/lib/utils';
import logger from '@/logger';

interface SkipLinkProps {
    href: string;
    children: React.ReactNode;
    className?: string;
}

/**
 * Individual Skip Link Component
 */
function SkipLink({ href, children, className }: SkipLinkProps) {
    const handleClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
        event.preventDefault();

        const target = document.querySelector(href);
        if (target instanceof HTMLElement) {
            target.focus();
            // Ensure the element is focusable
            if (!target.hasAttribute('tabindex')) {
                target.setAttribute('tabindex', '-1');
            }
            logger.info('SkipLink: Navigated to target', { href, target: target.tagName });
        } else {
            logger.warn('SkipLink: Target element not found', { href });
        }
    };

    return (
        <a
            href={href}
            onClick={handleClick}
            className={cn(
                // Hidden by default, visible on focus
                'absolute -top-40 left-6 z-50',
                // Use only Tailwind semantic color classes for background, text, and focus
                'bg-primary text-primary-foreground px-4 py-2 rounded-md',
                'text-sm font-medium',
                'focus:top-6 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                'transition-all duration-200',
                className
            )}
        >
            {children}
        </a>
    );
}

interface SkipLinksProps {
    links?: Array<{
        href: string;
        label: string;
    }>;
    className?: string;
}

/**
 * Default skip links for common page elements
 */
const DEFAULT_SKIP_LINKS = [
    { href: '#main-content', label: 'Skip to main content' },
    { href: '#navigation', label: 'Skip to navigation' },
    { href: '#footer', label: 'Skip to footer' }
];

/**
 * Skip Links Component
 * Renders accessibility skip links for keyboard navigation
 * 
 * @example
 * ```tsx
 * // Use default skip links
 * <SkipLinks />
 * 
 * // Custom skip links
 * <SkipLinks 
 *   links={[
 *     { href: '#content', label: 'Skip to content' },
 *     { href: '#sidebar', label: 'Skip to sidebar' }
 *   ]} 
 * />
 * ```
 */
export function SkipLinks({
    links = DEFAULT_SKIP_LINKS,
    className
}: SkipLinksProps) {
    React.useEffect(() => {
        logger.debug('SkipLinks: Rendered with links', {
            linkCount: links.length,
            links: links.map(link => link.href)
        });
    }, [links]);

    return (
        <nav
            aria-label="Skip navigation links"
            className={cn('skip-links', className)}
        >
            {links.map((link, index) => (
                <SkipLink
                    key={`${link.href}-${index}`}
                    href={link.href}
                    className={index > 0 ? 'left-auto right-6' : undefined}
                >
                    {link.label}
                </SkipLink>
            ))}
        </nav>
    );
}

/**
 * Hook for managing skip link targets
 * Ensures skip link targets have proper accessibility attributes
 */
export function useSkipLinkTargets(targets: string[]) {
    React.useEffect(() => {
        targets.forEach(target => {
            const element = document.querySelector(target);
            if (element instanceof HTMLElement) {
                // Ensure element can receive focus
                if (!element.hasAttribute('tabindex')) {
                    element.setAttribute('tabindex', '-1');
                }

                // Add aria-label for screen readers
                if (!element.hasAttribute('aria-label') && !element.hasAttribute('aria-labelledby')) {
                    const label = target.replace('#', '').replace(/-/g, ' ');
                    element.setAttribute('aria-label', label);
                }

                logger.debug('SkipLinks: Configured target element', {
                    target,
                    tagName: element.tagName
                });
            } else {
                logger.warn('SkipLinks: Target element not found', { target });
            }
        });
    }, [targets]);
}

/**
 * Enhanced Skip Links with auto-discovery
 * Automatically discovers common page landmarks
 */
export function EnhancedSkipLinks({ className }: { className?: string }) {
    const [discoveredLinks, setDiscoveredLinks] = React.useState<Array<{
        href: string;
        label: string;
    }>>([]);

    React.useEffect(() => {
        const discoverLinks = () => {
            const links: Array<{ href: string; label: string }> = [];

            // Common landmarks to look for
            const landmarks = [
                { selector: 'main, [role="main"], #main, #main-content', label: 'Skip to main content' },
                { selector: 'nav, [role="navigation"], #navigation', label: 'Skip to navigation' },
                { selector: 'aside, [role="complementary"], #sidebar', label: 'Skip to sidebar' },
                { selector: 'footer, [role="contentinfo"], #footer', label: 'Skip to footer' },
                { selector: '[role="search"], #search', label: 'Skip to search' }
            ];

            landmarks.forEach(landmark => {
                const element = document.querySelector(landmark.selector);
                if (element) {
                    let href = `#${element.id}`;

                    // Generate ID if element doesn't have one
                    if (!element.id) {
                        const generatedId = landmark.selector.split(',')[0]
                            .replace(/[^\w-]/g, '')
                            .replace(/^[^a-zA-Z]/, 'landmark-');
                        element.id = generatedId;
                        href = `#${generatedId}`;
                    }

                    links.push({
                        href,
                        label: landmark.label
                    });
                }
            });

            setDiscoveredLinks(links);
            logger.info('SkipLinks: Discovered page landmarks', {
                count: links.length,
                links: links.map(l => l.href)
            });
        };

        // Discover links after DOM is ready
        const timer = setTimeout(discoverLinks, 100);
        return () => clearTimeout(timer);
    }, []);

    if (discoveredLinks.length === 0) {
        // Fallback to default links
        return <SkipLinks className={className} />;
    }

    return <SkipLinks links={discoveredLinks} className={className} />;
}
