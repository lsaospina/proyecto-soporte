import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TempPasswordModal } from '../components/TempPasswordModal';

describe('TempPasswordModal', () => {
  it('does not render when closed', () => {
    render(<TempPasswordModal open={false} password="Abc123!@#xyz" onClose={() => {}} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('renders password and calls onClose', () => {
    const onClose = vi.fn();
    Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
    render(<TempPasswordModal open password="Abc123!@#xyz" onClose={onClose} />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Abc123!@#xyz')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /ya la guardé/i }));
    expect(onClose).toHaveBeenCalled();
  });
});
