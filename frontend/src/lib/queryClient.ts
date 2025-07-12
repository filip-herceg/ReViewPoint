import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			retry: 1,
			refetchOnWindowFocus: false,
			staleTime: 1000 * 60, // 1 minute
			// To handle errors globally, use queryCache.on('error', ...) or handle in each hook/component
		},
		mutations: {
			retry: 0,
			// To handle errors globally, use mutationCache.on('error', ...) or handle in each hook/component
		},
	},
});
