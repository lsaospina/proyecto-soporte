import { z } from 'zod';

const MAC_RE = /^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$/;

function hoyISO(): string {
  const d = new Date();
  const mes = String(d.getMonth() + 1).padStart(2, '0');
  const dia = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${mes}-${dia}`;
}

export const activoSchema = z.object({
  serial: z.string().trim().min(1, 'El serial es obligatorio').max(120),
  modelo: z.number().min(1, 'El modelo es obligatorio'),
  fecha_adquisicion: z
    .string()
    .min(1, 'La fecha es obligatoria')
    .refine((v) => v <= hoyISO(), 'La fecha no puede ser futura'),
  valor_adquisicion: z.string().optional(),
  procesador: z.string().optional(),
  ram_gb: z.union([z.number().positive(), z.null()]).optional(),
  almacenamiento_gb: z.union([z.number().positive(), z.null()]).optional(),
  direccion_mac: z
    .string()
    .optional()
    .refine((v) => !v || MAC_RE.test(v), 'Formato de MAC inválido (AA:BB:CC:DD:EE:FF)'),
  observaciones: z.string().optional(),
});
export type ActivoFormData = z.infer<typeof activoSchema>;