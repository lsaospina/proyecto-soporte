import type { CSSProperties } from 'react';

export function estiloCampo(error = false): CSSProperties {
  return {
    width: '100%',
    padding: '8px 10px',
    fontSize: '14px',
    color: 'var(--text)',
    backgroundColor: 'var(--surface-lowest)',
    border: `1px solid ${error ? 'var(--danger-fg)' : 'var(--border)'}`,
    borderRadius: 'var(--radius-control)',
  };
}
