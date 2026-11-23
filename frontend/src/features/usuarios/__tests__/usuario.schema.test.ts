import { describe, it, expect } from 'vitest';
import { usuarioSchema, usuarioUpdateSchema } from '../schemas/usuario.schema';

describe('usuarioSchema', () => {
  it('accepts valid user payload', () => {
    const result = usuarioSchema.safeParse({
      email: 'nuevo@empresa.com',
      nombre_completo: 'Nuevo Usuario',
      rol: 'TECNICO',
    });
    expect(result.success).toBe(true);
  });

  it('rejects invalid email', () => {
    const result = usuarioSchema.safeParse({
      email: 'invalido',
      nombre_completo: 'Nombre',
      rol: 'TECNICO',
    });
    expect(result.success).toBe(false);
  });

  it('rejects missing nombre_completo', () => {
    const result = usuarioSchema.safeParse({
      email: 'a@b.com',
      nombre_completo: '',
      rol: 'ADMINISTRADOR',
    });
    expect(result.success).toBe(false);
  });

  it('update schema does not require email', () => {
    const result = usuarioUpdateSchema.safeParse({
      nombre_completo: 'Editado',
      rol: 'USUARIO_RESPONSABLE',
    });
    expect(result.success).toBe(true);
  });
});
