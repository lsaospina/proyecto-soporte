import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { CatalogosPage } from '../pages/CatalogosPage';

vi.mock('../api/catalogos.api', () => ({
  catalogosApi: {
    list: vi.fn().mockResolvedValue({ count: 1, next: null, previous: null, results: [{ id: 1, nombre: 'Sede A', is_active: true }] }),
    create: vi.fn(),
    update: vi.fn(),
  },
}));

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}><MemoryRouter><CatalogosPage /></MemoryRouter></QueryClientProvider>);
}

describe('CatalogosPage smoke', () => {
  it('renders', async () => {
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });
});