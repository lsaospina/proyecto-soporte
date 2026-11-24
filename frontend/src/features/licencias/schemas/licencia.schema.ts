import { z } from 'zod';

import { aISO } from '../../../lib/format';

const fecha = z.string().min(1, 'La fecha es obligatoria');

const valorOpcional = z
  .string()
  .trim()
  .refine(
    (valor) => valor === '' || (!Number.isNaN(Number(valor)) && Number(valor) >= 0),
    'Ingrese un valor mayor o igual a cero',
  );

export const licenciaSchema = z.object({
  proveedor: z.string().trim().min(1, 'El proveedor es obligatorio').max(120),
  servicio: z.string().trim().min(2, 'El servicio es obligatorio').max(160),
  periodicidad: z.enum(['MENSUAL', 'TRIMESTRAL', 'SEMESTRAL', 'ANUAL', 'BIENAL']),
  fecha_renovacion: fecha,
  cantidad: z.coerce
    .number({ message: 'La cantidad es obligatoria' })
    .int('Debe ser un número entero')
    .min(1, 'La cantidad mínima es 1'),
  valor: valorOpcional,
  renovacion_automatica: z.boolean(),
  medio_pago: z.string().trim().max(160),
  cuenta_vinculada: z.string().trim().max(160),
  responsable_uso: z.string().trim().max(200),
  observacion: z.string().trim().max(1000),
});

export type LicenciaFormData = z.infer<typeof licenciaSchema>;

export const renovarLicenciaSchema = z
  .object({
    fecha_renovacion: fecha,
    valor: valorOpcional,
  })
  .refine((datos) => datos.fecha_renovacion >= aISO(new Date()), {
    path: ['fecha_renovacion'],
    message: 'La nueva fecha debe ser hoy o posterior',
  });

export type RenovarLicenciaFormData = z.infer<typeof renovarLicenciaSchema>;
