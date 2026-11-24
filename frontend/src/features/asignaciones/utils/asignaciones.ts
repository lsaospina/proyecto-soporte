import type { CSSProperties } from 'react';

export const ETIQUETA_ROL: Record<string, string> = {
  ADMINISTRADOR: 'Administrador',
  TECNICO: 'Técnico',
  USUARIO_RESPONSABLE: 'Usuario responsable',
};

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

export function textoDuracion(dias: number): string {
  if (dias === 0) return 'Menos de un día';
  return `${dias} día${dias === 1 ? '' : 's'}`;
}
