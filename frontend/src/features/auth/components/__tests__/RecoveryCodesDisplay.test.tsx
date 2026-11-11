import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RecoveryCodesDisplay } from '../RecoveryCodesDisplay';

describe('RecoveryCodesDisplay', () => {
  const sampleCodes = ['CODE1111', 'CODE2222', 'CODE3333', 'CODE4444'];

  it('renders all recovery codes', () => {
    render(<RecoveryCodesDisplay codes={sampleCodes} onContinue={() => {}} />);
    sampleCodes.forEach((code) => {
      expect(screen.getByText(code)).toBeInTheDocument();
    });
  });

  it('calls onContinue callback when continue button is clicked', () => {
    const handleContinue = vi.fn();
    render(<RecoveryCodesDisplay codes={sampleCodes} onContinue={handleContinue} />);
    const continueBtn = screen.getByRole('button', { name: /continuar/i });
    fireEvent.click(continueBtn);
    expect(handleContinue).toHaveBeenCalledTimes(1);
  });
});
