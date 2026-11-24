export type EstadoActivo = 'DISPONIBLE' | 'ASIGNADO' | 'EN_MANTENIMIENTO' | 'DADO_DE_BAJA';

export interface ActivoBreve {
  id: number;
  serial: string;
  codigo_qr: string;
  marca: string;
  modelo: string;
  categoria: string;
  estado: EstadoActivo;
  fecha_adquisicion: string;
}

export interface EstadoActivoResumen {
  estado: EstadoActivo;
  etiqueta: string;
  total: number;
}

export interface GrupoActivoResumen {
  nombre: string;
  total: number;
}

export interface ActivosResumen {
  total: number;
  operativos: number;
  en_mantenimiento: number;
  dados_de_baja: number;
  inactivos: number;
  valor_total: string | null;
  por_estado: EstadoActivoResumen[];
  por_categoria: GrupoActivoResumen[];
  por_marca: GrupoActivoResumen[];
  ultimas_adquisiciones: ActivoBreve[];
}

export interface MantenimientoBreve {
  id: number;
  activo_serial: string;
  activo_codigo: string;
  marca: string;
  modelo: string;
  tipo: 'PREVENTIVO' | 'CORRECTIVO';
  fecha_programada: string;
  tecnico: string | null;
  observacion: string;
  dias_restantes?: number;
  dias_atraso?: number;
}

export interface PreventivosAnio {
  total: number;
  agendados: number;
  cancelados: number;
  completados: number;
  vencidos: number;
  incumplidos: number;
  pendientes: number;
  porcentaje_cumplimiento: number;
}

export interface MesResumen {
  mes: number;
  agendados: number;
  completados: number;
  vencidos: number;
  incumplidos: number;
  porcentaje_cumplimiento: number;
}

export interface CorrectivosResumen {
  registrados_30_dias: number;
  costo_30_dias: string;
  recientes: MantenimientoBreve[];
}

export interface ActivosSinPreventivo {
  total: number;
  activos: ActivoBreve[];
}

export interface MantenimientosResumen {
  preventivos_anio: PreventivosAnio;
  mensual: MesResumen[];
  proximos: MantenimientoBreve[];
  vencidos: MantenimientoBreve[];
  correctivos: CorrectivosResumen;
  activos_sin_preventivo: ActivosSinPreventivo;
  costo_anio: string;
}

export interface DashboardResumen {
  hoy: string;
  anio: number;
  activos: ActivosResumen;
  mantenimientos: MantenimientosResumen | null;
}
