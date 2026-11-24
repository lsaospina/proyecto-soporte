import { describe, expect, it } from 'vitest';

import { aISO } from '../../../../lib/format';
import { licenciaSchema, renovarLicenciaSchema } from '../licencia.schema';

function datosValidos(overrides: Record<string, unknown> = {}) {
  return {
    proveedor: 'Microsoft',
    servicio: 'Microsoft 365 Familia',
    periodicidad: 'ANUAL',
    fecha_renovacion: '2026-12-01',
    cantidad: '6',
    valor: '459999.00',
    renovacion_automatica: true,
    medio_pago: 'Facturación electrónica',
    cuenta_vinculada: 'admin@empresa.com',
    responsable_uso: 'Equipo administrativo',
    observacion: '',
    ...overrides,
  };
}

describe('licenciaSchema', () => {
  it('convierte la cantidad y acepta valor vacío', () => {
    const resultado = licenciaSchema.safeParse(datosValidos({ valor: '' }));
    expect(resultado.success).toBe(true);
    if (resultado.success) {
      expect(resultado.data.cantidad).toBe(6);
      expect(resultado.data.valor).toBe('');
    }
  });

  it('rechaza proveedor vacío, cantidad cero y valor negativo', () => {
    const resultado = licenciaSchema.safeParse(
      datosValidos({ proveedor: '  ', cantidad: '0', valor: '-5' }),
    );
    expect(resultado.success).toBe(false);
    if (!resultado.success) {
      const campos = resultado.error.issues.map((issue) => issue.path[0]);
      expect(campos).toContain('proveedor');
      expect(campos).toContain('cantidad');
      expect(campos).toContain('valor');
    }
  });
});

describe('renovarLicenciaSchema', () => {
  it('acepta hoy o una fecha futura', () => {
    expect(
      renovarLicenciaSchema.safeParse({ fecha_renovacion: aISO(new Date()), valor: '' }).success,
    ).toBe(true);
    expect(
      renovarLicenciaSchema.safeParse({ fecha_renovacion: '2099-01-01', valor: '100' }).success,
    ).toBe(true);
  });

  it('rechaza una fecha pasada', () => {
    const resultado = renovarLicenciaSchema.safeParse({
      fecha_renovacion: '2020-01-01',
      valor: '',
    });
    expect(resultado.success).toBe(false);
  });
});
