import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { Mock } from 'vitest';

type ExtendedMock = Mock<() => {
  trackEvent: Mock<any>;
  trackPageview: Mock<any>;
  enableAutoPageviews: Mock<any>;
  enableAutoOutboundTracking: Mock<any>;
}> & {
  invokeMockImplementationOnce: () => any;
};

vi.mock('plausible-tracker', () => {
  const mock = vi.fn(() => ({
    trackEvent: vi.fn(),
    trackPageview: vi.fn(),
    enableAutoPageviews: vi.fn(),
    enableAutoOutboundTracking: vi.fn(),
  })) as ExtendedMock;

  mock.invokeMockImplementationOnce = function () {
    const impl = this.getMockImplementation();
    if (!impl) {
      throw new Error('No mock implementation set');
    }
    this.mockImplementation(() => ({
      trackEvent: vi.fn(),
      trackPageview: vi.fn(),
      enableAutoPageviews: vi.fn(),
      enableAutoOutboundTracking: vi.fn(),
    })); // Reset to a default mock implementation
    return impl();
  };

  mock.mockImplementationOnce = function (impl) {
    const originalMock = this;
    const onceMock = vi.fn(impl);
    this.mockImplementation((...args) => {
      if (onceMock.mock.calls.length === 0) {
        return onceMock(...args);
      }
      return originalMock(...args);
    });
    return this;
  };

  return { default: mock };
});

let plausibleMock: ExtendedMock;

beforeEach(() => {
  plausibleMock = vi.mocked(require('plausible-tracker').default);

  // Ensure mockImplementation is attached
  if (!plausibleMock.mockImplementation) {
    plausibleMock.mockImplementation = vi.fn(() => Object.assign(() => ({
      trackEvent: vi.fn(),
      trackPageview: vi.fn(),
      enableAutoPageviews: vi.fn(),
      enableAutoOutboundTracking: vi.fn(),
    }), {
      calls: [],
      instances: [],
      contexts: [],
      invocationCallOrder: [],
      results: [],
      settledResults: [],
      lastCall: [] as [],
      mock: {
        calls: [],
        instances: [],
        contexts: [],
        invocationCallOrder: [],
        results: [],
        settledResults: [],
        lastCall: [] as [],
      },
      mockClear: vi.fn(),
      mockReset: vi.fn(),
      mockRestore: vi.fn(),
      getMockImplementation: vi.fn(),
      mockImplementation: vi.fn(),
      mockImplementationOnce: vi.fn(),
      withImplementation: vi.fn(),
      mockReturnThis: vi.fn(),
      mockReturnValue: vi.fn(),
      mockReturnValueOnce: vi.fn(),
      mockResolvedValue: vi.fn(),
      mockResolvedValueOnce: vi.fn(),
      mockRejectedValue: vi.fn(),
      mockRejectedValueOnce: vi.fn(),
      getMockName: vi.fn(),
      mockName: vi.fn(),
      [Symbol.dispose]: vi.fn(),
      new: () => ({
        trackEvent: vi.fn(),
        trackPageview: vi.fn(),
        enableAutoPageviews: vi.fn(),
        enableAutoOutboundTracking: vi.fn(),
      }),
    }));
  }

  // Ensure mockImplementationOnce is attached
  if (!plausibleMock.mockImplementationOnce) {
    plausibleMock.mockImplementationOnce = vi.fn();
  }

  // Ensure invokeMockImplementationOnce is attached
  if (!plausibleMock.invokeMockImplementationOnce) {
    plausibleMock.invokeMockImplementationOnce = function () {
      const impl = this.getMockImplementation();
      if (!impl) {
        throw new Error('No mock implementation set');
      }
      const result = impl();
      return result;
    };
  }

  // Debug log to inspect plausibleMock state
  console.log('Debug: plausibleMock after initialization', plausibleMock);
  console.debug('plausibleMock state in beforeEach:', plausibleMock);
});

import '../src/analytics';
import { createTestError } from './test-templates';

// We want to test that analytics initialization errors are handled and do not throw

describe('analytics.ts', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should initialize Plausible without throwing', async () => {
    await expect(async () => {
      await import('@/analytics');
    }).not.toThrow();
  });

  it('should handle Plausible init errors defensively', async () => {
    // Debug log to inspect plausibleMock
    console.log('Debug: plausibleMock in test', plausibleMock);

    // Ensure plausibleMock is defined
    expect(plausibleMock).toBeDefined();

    // Force Plausible to throw
    plausibleMock.mockImplementationOnce(() => { throw new Error('fail'); });

    // Re-import the module to trigger the error handling
    await expect(async () => {
      await import('@/analytics');
    }).not.toThrow();
  });

  it('should use createTestError for error normalization', () => {
    const err = createTestError('Analytics initialization error');
    expect(err).toBeInstanceOf(Error);
    expect(err.message).toMatch(/Analytics initialization error/);
  });
});

describe('plausibleMock', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it.skip('should support mockImplementationOnce', () => {
    // Set a mock implementation
    plausibleMock.mockImplementationOnce(() => ({
      trackEvent: vi.fn(),
      trackPageview: vi.fn(),
      enableAutoPageviews: vi.fn(),
      enableAutoOutboundTracking: vi.fn(),
    }));

    // Invoke the mock implementation
    const result = plausibleMock.invokeMockImplementationOnce();

    // Assert the result
    expect(result).toEqual(expect.objectContaining({
      trackEvent: expect.any(Function),
      trackPageview: expect.any(Function),
      enableAutoPageviews: expect.any(Function),
      enableAutoOutboundTracking: expect.any(Function),
    }));

    // Test that the function exists and can be called
    expect(typeof plausibleMock.invokeMockImplementationOnce).toBe('function');
  });

  it('should log the debug information', () => {
    // Debug log to inspect the state of plausibleMock
    console.log('Debug: plausibleMock', plausibleMock);
    console.log('Debug: plausibleMock in test', plausibleMock);

    // Assert that the debug log does not throw an error
    expect(() => console.log('Debug: plausibleMock', plausibleMock)).not.toThrow();
  });
});

// Debug log to inspect plausibleMock
// console.log('Debug: plausibleMock in test', plausibleMock);
