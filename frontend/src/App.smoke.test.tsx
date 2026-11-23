import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

describe('App smoke', () => {
  it('renders without ErrorBoundary', () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <App />
      </QueryClientProvider>,
    );
    expect(screen.queryByText('Ha ocurrido un error inesperado.')).not.toBeInTheDocument();
  });
});
