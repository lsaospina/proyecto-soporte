import { z } from 'zod';

import { aISO } from '../../../lib/format';

const fecha = z.string().min(1, 'La fecha es obligatoria');

export const asignarSchema = z.object({
  activo: z.coerce.number({ message: 'Seleccione un equipo' }).int().min(1, 'Seleccione un equipo'),
  usuario: z.coerce
    .number({ message: 'Seleccione un colaborador' })
    .int()
    .min(1, 'Seleccione un colaborador'),
  fecha_inicio: fecha,
  observacion: z.string().trim().max(500),
});

export type AsignarFormData = z.infer<typeof asignarSchema>;

export const reasignarSchema = asignarSchema.omit({ activo: true });
export type ReasignarFormData = z.infer<typeof reasignarSchema>;

export function cerrarSchema(fechaInicio: string) {
  return z
    .object({
      fecha_fin: fecha,
    })
    .refine((datos) => datos.fecha_fin >= fechaInicio, {
      path: ['fecha_fin'],
      message: 'La devolución no puede ser anterior al inicio de la asignación',
    })
    .refine((datos) => datos.fecha_fin <= aISO(new Date()), {
      path: ['fecha_fin'],
      message: 'La devolución no puede ser futura',
    });
}

export type CerrarFormData = z.infer<ReturnType<typeof cerrarSchema>>;
