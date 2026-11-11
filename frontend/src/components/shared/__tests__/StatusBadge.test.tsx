import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '../StatusBadge';

describe('StatusBadge', () => {
  it('renders children text correctly', () => {
    render(<StatusBadge variant="success">Activo</StatusBadge>);
    expect(screen.getByText('Activo')).toBeInTheDocument();
  });

  it('renders with correct variant styles', () => {
    const { container } = render(<StatusBadge variant="danger">Baja</StatusBadge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toBeInTheDocument();
    expect(badge.tagName).toBe('SPAN');
  });

  it('renders dot indicator by default', () => {
    const { container } = render(<StatusBadge variant="warning">Mantenimiento</StatusBadge>);
    const dot = container.querySelector('span > span');
    expect(dot).toBeInTheDocument();
  });

  it('does not render dot indicator when dot={false}', () => {
    const { container } = render(
      <StatusBadge variant="neutral" dot={false}>
        Borrador
      </StatusBadge>
    );
    const dots = container.querySelectorAll('span > span');
    expect(dots.length).toBe(0);
  });
});
