import { z } from 'zod';

export const activoSchema = z.object({
  serial: z.string().trim().min(1, 'El serial es obligatorio').max(120),
  modelo: z.number().min(1, 'El modelo es obligatorio'),
  fecha_adquisicion: z.string().min(1, 'La fecha es obligatoria'),
  valor_adquisicion: z.string().optional(),
  procesador: z.string().optional(),
  ram_gb: z.union([z.number().positive(), z.null()]).optional(),
  almacenamiento_gb: z.union([z.number().positive(), z.null()]).optional(),
  direccion_mac: z.string().optional(),
  observaciones: z.string().optional(),
});
export type ActivoFormData = z.infer<typeof activoSchema>;