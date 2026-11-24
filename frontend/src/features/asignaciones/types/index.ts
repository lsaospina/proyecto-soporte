export interface Asignacion {
  id: number;
  activo: number;
  activo_serial: string;
  activo_codigo: string;
  marca_nombre: string;
  modelo_nombre: string;
  categoria_nombre: string;
  usuario: number;
  usuario_nombre: string;
  usuario_email: string;
  asignado_por: number;
  asignado_por_nombre: string;
  fecha_inicio: string;
  fecha_fin: string | null;
  activa: boolean;
  dias_asignado: number;
  observacion: string;
  created_at: string;
  updated_at: string;
}

export interface AsignacionPayload {
  activo: number;
  usuario: number;
  fecha_inicio?: string | null;
  observacion?: string;
}

export interface ReasignarPayload {
  activo: number;
  usuario: number;
  fecha_inicio?: string | null;
  observacion?: string;
}

export interface CerrarPayload {
  fecha_fin?: string | null;
}

export interface UsuarioAsignable {
  id: number;
  nombre_completo: string;
  email: string;
  rol: string;
}

export interface ResumenAsignaciones {
  hoy: string;
  activos_operativos: number;
  asignados: number;
  disponibles: number;
  en_mantenimiento: number;
  colaboradores: number;
  asignaciones_historicas: number;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
