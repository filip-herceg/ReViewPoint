# queryClient.ts - React Query Configuration

## Purpose

Central configuration for TanStack React Query client, managing global query and mutation defaults for the entire application's data fetching layer.

## Key Components

### QueryClient Configuration

- **Retry Strategy**: Single retry for failed queries to balance reliability with performance
- **Refetch Behavior**: Disabled window focus refetching to prevent unnecessary network requests
- **Stale Time**: 1-minute cache duration for data freshness optimization
- **Error Handling**: Configured for global error management at component level

### Performance Optimizations

- Conservative retry policies (1 for queries, 0 for mutations)
- Intelligent stale time management for reduced API calls
- Window focus refetch disabled for better user experience

## Configuration Details

```typescript
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60, // 1 minute
    },
    mutations: {
      retry: 0,
    },
  },
});
```

## Usage Context

- Imported and used in `main.tsx` for application-wide query management
- Provides consistent data fetching behavior across all components
- Centralized configuration for caching and network policies

## Integration Points

- **React Provider**: Wrapped around entire app in `main.tsx`
- **Error Handling**: Integrated with component-level error boundaries
- **Performance**: Coordinates with monitoring for query performance tracking

## Best Practices

- Global configuration reduces boilerplate in individual queries
- Conservative retry policies prevent API overload
- Stale time balances fresh data with performance
- Error handling delegated to components for context-specific responses

## Related Files

- [`main.tsx`](../main.tsx.md) - QueryClient provider setup
- [`lib/api/`](api/base.ts.md) - API client integration
- [`hooks/`](../../hooks/) - Custom query hooks implementation
