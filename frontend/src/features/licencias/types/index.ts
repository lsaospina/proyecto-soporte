export type Periodicidad = 'MENSUAL' | 'TRIMESTRAL' | 'SEMESTRAL' | 'ANUAL' | 'BIENAL';

export type EstadoRenovacion = 'VIGENTE' | 'POR_VENCER' | 'VENCIDA' | 'INACTIVA';

export interface Licencia {
  id: number;
  proveedor: number;
  proveedor_nombre: string;
  servicio: string;
  periodicidad: Periodicidad;
  fecha_renovacion: string;
  cantidad: number;
  valor: string | null;
  renovacion_automatica: boolean;
  medio_pago: string;
  cuenta_vinculada: string;
  responsable_uso: string;
  observacion: string;
  is_active: boolean;
  dias_para_renovacion: number;
  estado_renovacion: EstadoRenovacion;
  estado_renovacion_etiqueta: string;
  created_at: string;
  updated_at: string;
}

export interface LicenciaPayload {
  proveedor: string;
  servicio: string;
  periodicidad: Periodicidad;
  fecha_renovacion: string;
  cantidad: number;
  valor: string | null;
  renovacion_automatica: boolean;
  medio_pago: string;
  cuenta_vinculada: string;
  responsable_uso: string;
  observacion: string;
}

export interface RenovarPayload {
  fecha_renovacion: string;
  valor?: string | null;
}

export interface ProveedorOpcion {
  id: number;
  nombre: string;
}

export interface ResumenLicencias {
  hoy: string;
  total: number;
  activas: number;
  inactivas: number;
  por_vencer: number;
  vencidas: number;
  renovacion_automatica: number;
  costo_anual_estimado: string;
  costo_por_vencer: string;
  por_periodicidad: Array<{ periodicidad: Periodicidad; total: number }>;
  por_proveedor: Array<{ nombre: string; total: number }>;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
  hoy?: string;
}
