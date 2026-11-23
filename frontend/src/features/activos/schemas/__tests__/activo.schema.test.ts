import { describe, it, expect } from 'vitest';
import { activoSchema } from '../activo.schema';

describe('activoSchema', () => {
  it('válido', () => {
    expect(activoSchema.safeParse({ serial: 'SN1', modelo: 1, fecha_adquisicion: '2024-01-01' }).success).toBe(true);
  });
  it('serial vacío inválido', () => {
    expect(activoSchema.safeParse({ serial: '', modelo: 1, fecha_adquisicion: '2024-01-01' }).success).toBe(false);
  });
  it('modelo faltante inválido', () => {
    expect(activoSchema.safeParse({ serial: 'SN1', fecha_adquisicion: '2024-01-01' }).success).toBe(false);
  });
  it('fecha vacía inválida', () => {
    expect(activoSchema.safeParse({ serial: 'SN1', modelo: 1, fecha_adquisicion: '' }).success).toBe(false);
  });
});