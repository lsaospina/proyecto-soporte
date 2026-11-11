import { z } from 'zod';

export const mfaCodeSchema = z.object({
  code: z
    .string()
    .length(6, 'El código debe tener 6 dígitos')
    .regex(/^\d{6}$/, 'El código debe contener solo números'),
});

export const recoveryCodeSchema = z.object({
  recovery_code: z
    .string()
    .min(1, 'El código de recuperación es obligatorio'),
});

export type MFACodeFormData = z.infer<typeof mfaCodeSchema>;
export type RecoveryCodeFormData = z.infer<typeof recoveryCodeSchema>;
