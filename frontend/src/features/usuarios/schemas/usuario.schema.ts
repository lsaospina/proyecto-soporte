import { z } from 'zod';

export const usuarioSchema = z.object({
  email: z.string().min(1, 'El correo electrónico es obligatorio').email('Correo electrónico inválido'),
  nombre_completo: z.string().min(1, 'El nombre completo es obligatorio'),
  rol: z.enum(['ADMINISTRADOR', 'TECNICO', 'USUARIO_RESPONSABLE'], {
    message: 'Seleccione un rol válido',
  }),
});

export type UsuarioFormData = z.infer<typeof usuarioSchema>;

export const usuarioUpdateSchema = usuarioSchema.omit({ email: true });
export type UsuarioUpdateFormData = z.infer<typeof usuarioUpdateSchema>;
