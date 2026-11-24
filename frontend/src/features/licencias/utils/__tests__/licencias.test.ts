import { describe, expect, it } from 'vitest';

import { fechaRenovacion, sumarMeses, textoDias } from '../licencias';

describe('utilidades de licencias', () => {
  it('suma meses ajustando el fin de mes', () => {
    expect(sumarMeses('2026-01-31', 1)).toBe('2026-02-28');
    expect(sumarMeses('2026-01-15', 12)).toBe('2027-01-15');
    expect(sumarMeses('2026-06-30', 24)).toBe('2028-06-30');
  });

  it('describe los días de renovación', () => {
    expect(textoDias(0)).toBe('Vence hoy');
    expect(textoDias(1)).toBe('En 1 día');
    expect(textoDias(29)).toBe('En 29 días');
    expect(textoDias(-3)).toBe('Vencida hace 3 días');
    expect(fechaRenovacion('2026-12-01', 8)).toBe('01/12/2026 · En 8 días');
  });
});
