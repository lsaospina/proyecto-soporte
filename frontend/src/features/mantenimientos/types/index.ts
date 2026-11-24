export type Situacion =
  | 'PENDIENTE'
  | 'COMPLETADO'
  | 'VENCIDO'
  | 'INCUMPLIDO'
  | 'CANCELADO';

export interface Mantenimiento {
  id: number;
  activo: number;
  activo_serial: string;
  activo_codigo: string;
  marca_nombre: string;
  modelo_nombre: string;
  categoria_nombre: string;
  tipo: 'PREVENTIVO' | 'CORRECTIVO';
  fecha_programada: string;
  fecha_realizacion: string | null;
  fecha_seguimiento: string | null;
  tecnico: number | null;
  tecnico_nombre: string | null;
  costo: string | null;
  observacion: string;
  motivo_cancelacion: string;
  estado: 'PROGRAMADO' | 'COMPLETADO' | 'CANCELADO';
  situacion: Situacion;
  es_evidencia: boolean;
  reprogramado_como: number | null;
  reprogramacion_de: number | null;
  created_at: string;
  updated_at: string;
}

export interface ResumenMes {
  mes: number;
  agendados: number;
  completados: number;
  vencidos: number;
  incumplidos: number;
  porcentaje_cumplimiento: number;
}

export interface ResumenAnual {
  anio: number;
  hoy: string;
  meses: ResumenMes[];
}

export interface CalendarioMensual {
  anio: number;
  mes: number;
  hoy: string;
  mantenimientos: Mantenimiento[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
  hoy?: string;
}

export interface HistorialMantenimiento {
  fecha: string;
  usuario: string | null;
  tipo: string;
  campos: string[];
}
