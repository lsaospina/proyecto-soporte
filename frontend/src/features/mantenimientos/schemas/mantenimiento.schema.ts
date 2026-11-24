import { z } from 'zod';

const fecha = z.string().min(1, 'La fecha es obligatoria');

export const programarSchema = z.object({
  activo: z.number().min(1, 'El equipo es obligatorio'),
  fecha_programada: fecha,
  observacion: z.string().optional(),
});
export type ProgramarFormData = z.infer<typeof programarSchema>;

export const completarSchema = z.object({
  fecha_realizacion: fecha,
  tecnico: z.number().min(1, 'El técnico es obligatorio'),
  costo: z
    .string()
    .min(1, 'El costo es obligatorio')
    .refine((v) => !Number.isNaN(Number(v)) && Number(v) >= 0, 'El costo debe ser mayor o igual a cero'),
  observacion: z.string().optional(),
});
export type CompletarFormData = z.infer<typeof completarSchema>;

export const reprogramarSchema = z.object({
  fecha_programada: fecha,
});
export type ReprogramarFormData = z.infer<typeof reprogramarSchema>;

export const cancelarSchema = z.object({
  motivo: z.string().trim().min(1, 'El motivo es obligatorio'),
});
export type CancelarFormData = z.infer<typeof cancelarSchema>;
