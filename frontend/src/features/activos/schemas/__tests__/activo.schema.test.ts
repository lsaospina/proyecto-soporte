import { describe, it, expect } from 'vitest';
import { activoSchema } from '../activo.schema';

const base = { serial: 'SN1', modelo: 1, fecha_adquisicion: '2024-01-01' };

function mananaISO(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  const mes = String(d.getMonth() + 1).padStart(2, '0');
  const dia = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${mes}-${dia}`;
}

describe('activoSchema', () => {
  it('válido', () => {
    expect(activoSchema.safeParse({ ...base, direccion_mac: 'AA:BB:CC:DD:EE:FF' }).success).toBe(true);
  });
  it('serial vacío inválido', () => {
    expect(activoSchema.safeParse({ ...base, serial: '' }).success).toBe(false);
  });
  it('MAC inválida', () => {
    expect(activoSchema.safeParse({ ...base, direccion_mac: 'ZZ:BB:CC:DD:EE:FF' }).success).toBe(false);
  });
  it('RAM negativa inválida', () => {
    expect(activoSchema.safeParse({ ...base, ram_gb: -1 }).success).toBe(false);
  });
  it('fecha futura inválida', () => {
    expect(activoSchema.safeParse({ ...base, fecha_adquisicion: mananaISO() }).success).toBe(false);
  });
});
