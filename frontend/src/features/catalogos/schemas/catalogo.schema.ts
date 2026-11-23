import { z } from 'zod';

export const catalogoSchema = z.object({
  nombre: z.string().trim().min(1, 'El nombre es obligatorio').max(120),
  direccion: z.string().optional(),
  descripcion: z.string().optional(),
  sede: z.number().optional(),
  marca: z.number().optional(),
  categoria: z.number().optional(),
});
export type CatalogoFormData = z.infer<typeof catalogoSchema>;
