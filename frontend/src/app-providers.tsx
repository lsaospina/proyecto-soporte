import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './features/auth/hooks/useAuth';
import { Router } from './routes/Router';
import { ErrorBoundary } from './components/shared/ErrorBoundary';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } });

export function AppProviders({ children }: { children?: React.ReactNode }) {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          {children ?? <Router />}
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
