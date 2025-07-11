import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/button';
import { Link, BrowserRouter } from 'react-router-dom';
import React from 'react';

// Mock console methods to capture warnings
const mockConsoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});
const mockConsoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

describe('Button Component - React.Children.only Fixes', () => {
  beforeEach(() => {
    mockConsoleWarn.mockClear();
    mockConsoleError.mockClear();
  });

  it('renders standard button without asChild', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    expect(button).toBeInTheDocument();
    expect(button.tagName).toBe('BUTTON');
  });

  it('renders with asChild and single React element child', () => {
    render(
      <BrowserRouter>
        <Button asChild>
          <Link to="/test">Navigate</Link>
        </Button>
      </BrowserRouter>
    );
    
    const link = screen.getByRole('link', { name: 'Navigate' });
    expect(link).toBeInTheDocument();
    expect(link.tagName).toBe('A');
    expect(mockConsoleWarn).not.toHaveBeenCalled();
    expect(mockConsoleError).not.toHaveBeenCalled();
  });

  it('handles asChild with Link containing multiple child elements', () => {
    const ArrowIcon = () => <span>→</span>;
    
    render(
      <BrowserRouter>
        <Button asChild size="lg">
          <Link to="/auth/register" className="flex items-center">
            Get Started Free
            <ArrowIcon />
          </Link>
        </Button>
      </BrowserRouter>
    );
    
    // Should render successfully without React.Children.only error
    const link = screen.getByRole('link');
    expect(link).toBeInTheDocument();
    expect(link).toHaveTextContent('Get Started Free');
    expect(mockConsoleError).not.toHaveBeenCalled();
  });

  it('handles asChild with no children gracefully', () => {
    const { container } = render(<Button asChild />);
    
    // Should not crash, but may return null
    expect(container.firstChild).toBeNull();
    expect(mockConsoleWarn).toHaveBeenCalledWith(
      'Button asChild: No children provided. Component will not render.'
    );
  });

  it('handles asChild with invalid children gracefully', () => {
    const invalidChild = "just a string";
    
    const { container } = render(
      <Button asChild>
        {invalidChild}
      </Button>
    );
    
    // Should handle gracefully without crashing
    expect(mockConsoleWarn).toHaveBeenCalled();
  });

  it('applies correct variant classes', () => {
    render(<Button variant="destructive">Delete</Button>);
    
    const button = screen.getByRole('button', { name: 'Delete' });
    expect(button).toHaveClass('bg-destructive');
  });

  it('applies correct size classes', () => {
    render(<Button size="lg">Large Button</Button>);
    
    const button = screen.getByRole('button', { name: 'Large Button' });
    expect(button).toHaveClass('h-10');
  });

  it('shows loading state', () => {
    render(<Button loading>Saving...</Button>);
    
    const button = screen.getByRole('button', { name: 'Saving...' });
    expect(button).toBeDisabled();
    // Should have loading spinner (animated div)
    expect(button.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('handles disabled state', () => {
    render(<Button disabled>Disabled</Button>);
    
    const button = screen.getByRole('button', { name: 'Disabled' });
    expect(button).toBeDisabled();
  });

  it('forwards click events correctly', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('forwards click events with asChild correctly', () => {
    const handleClick = vi.fn();
    
    render(
      <BrowserRouter>
        <Button asChild>
          <Link to="/test" onClick={handleClick}>Navigate</Link>
        </Button>
      </BrowserRouter>
    );
    
    const link = screen.getByRole('link', { name: 'Navigate' });
    fireEvent.click(link);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not show loading spinner when asChild is true', () => {
    render(
      <BrowserRouter>
        <Button asChild loading>
          <Link to="/test">Loading Link</Link>
        </Button>
      </BrowserRouter>
    );
    
    const link = screen.getByRole('link', { name: 'Loading Link' });
    // Should not have loading spinner when asChild
    expect(link.querySelector('.animate-spin')).not.toBeInTheDocument();
  });

  it('combines custom className with variant classes', () => {
    render(<Button variant="outline" className="custom-class">Button</Button>);
    
    const button = screen.getByRole('button', { name: 'Button' });
    expect(button).toHaveClass('custom-class');
    expect(button).toHaveClass('border');
  });

  it('maintains accessibility attributes', () => {
    render(
      <Button 
        aria-label="Custom aria label" 
        data-testid="test-button"
        role="button"
      >
        Button
      </Button>
    );
    
    const button = screen.getByRole('button', { name: 'Custom aria label' });
    expect(button).toHaveAttribute('data-testid', 'test-button');
    expect(button).toHaveAttribute('aria-label', 'Custom aria label');
  });
});

describe('Button Component - Variant Coverage', () => {
  const variants = [
    'default',
    'destructive', 
    'outline',
    'outline-destructive',
    'outline-success',
    'secondary',
    'ghost',
    'link',
    'icon-sm',
    'tab',
    'theme-option',
    'floating-icon'
  ] as const;

  variants.forEach(variant => {
    it(`renders ${variant} variant correctly`, () => {
      render(<Button variant={variant}>Test {variant}</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      // Each variant should have its specific classes - we won't test exact classes
      // but ensure the component doesn't crash
    });
  });

  const sizes = ['sm', 'default', 'lg', 'icon', 'icon-sm', 'floating', 'none'] as const;

  sizes.forEach(size => {
    it(`renders ${size} size correctly`, () => {
      render(<Button size={size}>Test {size}</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });
});
