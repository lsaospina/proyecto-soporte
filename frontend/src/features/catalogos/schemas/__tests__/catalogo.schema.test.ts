import { describe, it, expect } from 'vitest';
import { catalogoSchema } from '../catalogo.schema';

describe('catalogoSchema', () => {
  it('válido', () => {
    expect(catalogoSchema.safeParse({ nombre: 'Sede A' }).success).toBe(true);
  });
  it('vacío inválido', () => {
    expect(catalogoSchema.safeParse({ nombre: '' }).success).toBe(false);
  });
  it('solo espacios inválido', () => {
    expect(catalogoSchema.safeParse({ nombre: '   ' }).success).toBe(false);
  });
  it('longitud excesiva inválida', () => {
    expect(catalogoSchema.safeParse({ nombre: 'a'.repeat(121) }).success).toBe(false);
  });
});
