import { describe, it, expect } from 'vitest';
import { mfaCodeSchema, recoveryCodeSchema } from '../mfa.schema';

describe('MFA Schemas', () => {
  describe('mfaCodeSchema', () => {
    it('accepts valid 6-digit numeric string', () => {
      const result = mfaCodeSchema.safeParse({ code: '123456' });
      expect(result.success).toBe(true);
    });

    it('rejects code shorter than 6 digits', () => {
      const result = mfaCodeSchema.safeParse({ code: '123' });
      expect(result.success).toBe(false);
    });

    it('rejects non-numeric characters', () => {
      const result = mfaCodeSchema.safeParse({ code: '12345a' });
      expect(result.success).toBe(false);
    });
  });

  describe('recoveryCodeSchema', () => {
    it('accepts valid 8-character alphanumeric recovery code', () => {
      const result = recoveryCodeSchema.safeParse({ recovery_code: 'A1B2C3D4' });
      expect(result.success).toBe(true);
    });

    it('rejects empty recovery code', () => {
      const result = recoveryCodeSchema.safeParse({ recovery_code: '' });
      expect(result.success).toBe(false);
    });
  });
});
