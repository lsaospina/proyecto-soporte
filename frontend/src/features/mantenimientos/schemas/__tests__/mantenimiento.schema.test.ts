import { describe, it, expect } from 'vitest';
import {
  cancelarSchema,
  completarSchema,
  correctivoSchema,
  programarSchema,
  reprogramarSchema,
} from '../mantenimiento.schema';

describe('mantenimiento schemas', () => {
  it('programar válido y sin equipo inválido', () => {
    expect(
      programarSchema.safeParse({ activo: 1, fecha_programada: '2026-11-20' }).success,
    ).toBe(true);
    expect(
      programarSchema.safeParse({ activo: 0, fecha_programada: '2026-11-20' }).success,
    ).toBe(false);
  });

  it('completar válido y costo negativo inválido', () => {
    expect(
      completarSchema.safeParse({
        fecha_realizacion: '2026-11-15',
        tecnico: 2,
        costo: '1500.50',
      }).success,
    ).toBe(true);
    expect(
      completarSchema.safeParse({
        fecha_realizacion: '2026-11-15',
        tecnico: 2,
        costo: '-1',
      }).success,
    ).toBe(false);
  });

  it('reprogramar exige fecha', () => {
    expect(reprogramarSchema.safeParse({ fecha_programada: '2026-12-10' }).success).toBe(true);
    expect(reprogramarSchema.safeParse({ fecha_programada: '' }).success).toBe(false);
  });

  it('cancelar exige motivo no vacío', () => {
    expect(cancelarSchema.safeParse({ motivo: 'Equipo retirado' }).success).toBe(true);
    expect(cancelarSchema.safeParse({ motivo: '   ' }).success).toBe(false);
  });

  it('correctivo válido, exige descripción y seguimiento posterior', () => {
    const base = {
      activo: 1,
      observacion: 'No enciende',
      fecha_programada: '2026-11-10',
      fecha_seguimiento: '2026-12-01',
    };
    expect(correctivoSchema.safeParse(base).success).toBe(true);
    expect(correctivoSchema.safeParse({ ...base, observacion: ' ' }).success).toBe(false);
    expect(correctivoSchema.safeParse({ ...base, fecha_seguimiento: '2026-11-01' }).success).toBe(
      false,
    );
  });
});
