import { describe, expect, it } from 'vitest';

import { aISO } from '../../../../lib/format';
import { asignarSchema, cerrarSchema } from '../asignacion.schema';

describe('asignarSchema', () => {
  it('acepta una asignación completa', () => {
    const resultado = asignarSchema.safeParse({
      activo: '12',
      usuario: '3',
      fecha_inicio: '2026-11-01',
      observacion: 'Entrega',
    });
    expect(resultado.success).toBe(true);
    if (resultado.success) {
      expect(resultado.data.activo).toBe(12);
      expect(resultado.data.usuario).toBe(3);
    }
  });

  it('rechaza equipo y colaborador vacíos', () => {
    const resultado = asignarSchema.safeParse({
      activo: '0',
      usuario: '',
      fecha_inicio: '',
      observacion: '',
    });
    expect(resultado.success).toBe(false);
    if (!resultado.success) {
      const campos = resultado.error.issues.map((issue) => issue.path[0]);
      expect(campos).toContain('activo');
      expect(campos).toContain('usuario');
      expect(campos).toContain('fecha_inicio');
    }
  });
});

describe('cerrarSchema', () => {
  it('acepta hoy y rechaza fechas anteriores al inicio o futuras', () => {
    const schema = cerrarSchema('2026-11-01');
    expect(schema.safeParse({ fecha_fin: aISO(new Date()) }).success).toBe(true);
    expect(schema.safeParse({ fecha_fin: '2026-10-31' }).success).toBe(false);
    expect(schema.safeParse({ fecha_fin: '2099-01-01' }).success).toBe(false);
  });
});
