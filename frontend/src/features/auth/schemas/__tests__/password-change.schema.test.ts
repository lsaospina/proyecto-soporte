import { describe, it, expect } from 'vitest';
import { passwordChangeSchema } from '../login.schema';

describe('passwordChangeSchema', () => {
  it('accepts matching passwords with min length', () => {
    const result = passwordChangeSchema.safeParse({
      new_password: 'NuevaPass123!',
      confirm_password: 'NuevaPass123!',
    });
    expect(result.success).toBe(true);
  });

  it('rejects non-matching passwords', () => {
    const result = passwordChangeSchema.safeParse({
      new_password: 'NuevaPass123!',
      confirm_password: 'OtraPass123!',
    });
    expect(result.success).toBe(false);
  });

  it('rejects short password', () => {
    const result = passwordChangeSchema.safeParse({
      new_password: 'short',
      confirm_password: 'short',
    });
    expect(result.success).toBe(false);
  });
});
